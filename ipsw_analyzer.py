#!/usr/bin/env python3
"""Read-only IPSW manifest and Mach-O metadata analyzer.

Reads BuildManifest.plist and selected component bytes from the IPSW ZIP in
memory. It does not decrypt, unpack compressed kernel caches, execute, patch,
restore, or communicate with a device.
"""
from __future__ import annotations
import argparse, hashlib, json, plistlib, struct, zipfile
from pathlib import Path
from typing import Any

VERSION = "0.8"
TARGET_PRODUCT = "iPhone13,2"
TARGET_BUILD = "24A437"
TARGET_CHIP_ID = 0x8101
# Apple BuildManifest component names of interest; this is metadata only.
INTERESTING_COMPONENTS = {
    "KernelCache", "DeviceTree", "iBoot", "LLB", "SEP", "RestoreRamDisk",
    "OS", "SystemVolume", "Cryptex1,SystemOS", "Cryptex1,AppOS",
}
MACHO_MAGICS = {
    b'\xfe\xed\xfa\xce': ('32-bit', '>'), b'\xce\xfa\xed\xfe': ('32-bit', '<'),
    b'\xfe\xed\xfa\xcf': ('64-bit', '>'), b'\xcf\xfa\xed\xfe': ('64-bit', '<'),
}
FAT_MAGICS = {b'\xca\xfe\xba\xbe': ('>', False), b'\xbe\xba\xfe\xca': ('<', False),
              b'\xca\xfe\xba\xbf': ('>', True), b'\xbf\xba\xfe\xca': ('<', True)}
CPU_TYPES = {7: 'x86', 12: 'ARM', 0x0100000C: 'ARM64', 0x01000007: 'x86_64'}
FILE_TYPES = {1:'OBJECT',2:'EXECUTE',3:'FVMLIB',4:'CORE',5:'PRELOAD',6:'DYLIB',7:'DYLINKER',8:'BUNDLE',9:'DYLIB_STUB',10:'DSYM',11:'KEXT_BUNDLE'}

def _str(v: Any) -> str | None:
    return str(v) if isinstance(v, (str,int)) else None

def _int(v: Any) -> int | None:
    if isinstance(v, int): return v
    if isinstance(v, str):
        try: return int(v, 0)
        except ValueError: return None
    return None

def _hex(v: Any) -> str | None:
    n=_int(v)
    return f"0x{n:x}" if n is not None else None

def _identity_records(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    out=[]
    for index, ident in enumerate(manifest.get('BuildIdentities', [])):
        if not isinstance(ident,dict): continue
        info=ident.get('Info',{}) if isinstance(ident.get('Info',{}),dict) else {}
        manifest_components=ident.get('Manifest',{}) if isinstance(ident.get('Manifest',{}),dict) else {}
        components=[]
        for name, details in sorted(manifest_components.items()):
            if name not in INTERESTING_COMPONENTS or not isinstance(details,dict): continue
            ci=details.get('Info',{}) if isinstance(details.get('Info',{}),dict) else {}
            components.append({'component':name,'path':_str(ci.get('Path')),
                'digest_present':bool(details.get('Digest')),'encrypted_flag':details.get('IsEncrypted'),
                'trusted_flag':details.get('Trusted')})
        out.append({'index':index,'device_class':_str(info.get('DeviceClass')),
            'variant':_str(info.get('Variant')),'restore_behavior':_str(info.get('RestoreBehavior')),
            'ap_chip_id':_int(ident.get('ApChipID')),'ap_chip_id_hex':_hex(ident.get('ApChipID')),
            'ap_board_id':_int(ident.get('ApBoardID')),'ap_board_id_hex':_hex(ident.get('ApBoardID')),
            'ap_security_domain':_int(ident.get('ApSecurityDomain')),
            'ap_production_mode':ident.get('ApProductionMode'),
            'ap_security_mode':ident.get('ApSecurityMode'),
            'components':components})
    return out

def _read_macho_header(data: bytes) -> dict[str, Any]:
    """Parse a bounded Mach-O header and selected load commands; no code execution."""
    if len(data)<4: return {'format':'unknown','reason':'too_short'}
    if data[:4] in FAT_MAGICS:
        endian,is64=FAT_MAGICS[data[:4]]
        if len(data)<8: return {'format':'fat','reason':'truncated_header'}
        nfat=struct.unpack_from(endian+'I',data,4)[0]
        if nfat>64: return {'format':'fat','reason':'unreasonable_arch_count','architecture_count':nfat}
        entry_size=32 if is64 else 20
        if 8+nfat*entry_size>len(data): return {'format':'fat','reason':'truncated_arch_table','architecture_count':nfat}
        archs=[]
        for i in range(nfat):
            off=8+i*entry_size
            if is64:
                cputype,cpusubtype,offset,size,align,res=struct.unpack_from(endian+'iiQQII',data,off)
            else:
                cputype,cpusubtype,offset,size,align=struct.unpack_from(endian+'iiIII',data,off)
            archs.append({'cpu_type':cputype,'cpu_name':CPU_TYPES.get(cputype,'unknown'),
                'cpu_subtype':cpusubtype,'slice_offset':offset,'slice_size':size,'alignment':align})
        return {'format':'fat64' if is64 else 'fat','architecture_count':nfat,'architectures':archs,
                'note':'Fat header parsed; individual slices are not disassembled.'}
    if data[:4] not in MACHO_MAGICS:
        return {'format':'not_plain_macho_or_compressed','magic_hex':data[:4].hex(),
                'note':'Could be a compressed/encrypted kernel cache or another container; no decompression attempted.'}
    bits,endian=MACHO_MAGICS[data[:4]]
    header_size=32 if bits=='64-bit' else 28
    if len(data)<header_size: return {'format':'macho','reason':'truncated_header'}
    if bits=='64-bit':
        magic,cpu,sub,filetype,ncmds,sizeofcmds,flags,reserved=struct.unpack_from(endian+'IiiIIIII',data,0)
    else:
        magic,cpu,sub,filetype,ncmds,sizeofcmds,flags=struct.unpack_from(endian+'IiiIIII',data,0)
    result={'format':'Mach-O','bits':bits,'endianness':'little' if endian=='<' else 'big',
        'cpu_type':cpu,'cpu_name':CPU_TYPES.get(cpu,'unknown'),'cpu_subtype':sub,
        'file_type':FILE_TYPES.get(filetype,f'UNKNOWN_{filetype}'),'load_command_count':ncmds,
        'load_commands_bytes':sizeofcmds,'flags':flags,'uuid':None,'build_versions':[],'segments':[],'encryption':None,'code_signature':None,'load_command_parse':'complete','parsed_load_commands':0}
    if ncmds>4096 or header_size+sizeofcmds>len(data):
        result['load_command_parse']='skipped_invalid_or_truncated_command_area'
        return result
    pos=header_size
    for _ in range(ncmds):
        if pos+8>len(data):
            result['load_command_parse']='truncated_command_header'; break
        cmd,cmdsize=struct.unpack_from(endian+'II',data,pos)
        if cmdsize<8 or pos+cmdsize>len(data):
            result['load_command_parse']='invalid_or_truncated_command'; break
        if cmd==0x1b and cmdsize>=24: # LC_UUID
            result['uuid']=data[pos+8:pos+24].hex()
        elif cmd in (0x21,0x2c) and cmdsize >= (20 if cmd==0x21 else 24): # LC_ENCRYPTION_INFO(_64)
            cryptoff,cryptsize,cryptid=struct.unpack_from(endian+'III',data,pos+8)
            result['encryption']={'command':'LC_ENCRYPTION_INFO_64' if cmd==0x2c else 'LC_ENCRYPTION_INFO',
                'crypt_offset':cryptoff,'crypt_size':cryptsize,'crypt_id':cryptid,
                'encrypted_flag_indicated':cryptid != 0}
        elif cmd==0x1d and cmdsize>=16: # LC_CODE_SIGNATURE
            dataoff,datasize=struct.unpack_from(endian+'II',data,pos+8)
            result['code_signature']={'data_offset':dataoff,'data_size':datasize,'blob_present_in_inspected_prefix':dataoff+datasize<=len(data)}
        elif cmd in (0x32,0x31) and cmdsize>=24: # LC_BUILD_VERSION / LC_VERSION_MIN_*
            if cmd==0x32:
                platform,minos,sdk,ntools=struct.unpack_from(endian+'IIII',data,pos+8)
                result['build_versions'].append({'command':'LC_BUILD_VERSION','platform':platform,'minos_raw':minos,'sdk_raw':sdk,'tool_count':ntools})
            else:
                version,sdk=struct.unpack_from(endian+'II',data,pos+8)
                result['build_versions'].append({'command':f'0x{cmd:x}','version_raw':version,'sdk_raw':sdk})
        elif cmd in (0x19,0x1): # LC_SEGMENT_64 / LC_SEGMENT
            name=data[pos+8:pos+24].split(b'\0',1)[0].decode('ascii','replace')
            result['segments'].append(name)
        result['parsed_load_commands'] += 1
        pos+=cmdsize
    if result['load_command_parse']=='complete' and result['parsed_load_commands'] != ncmds:
        result['load_command_parse']='command_count_mismatch'
    result['security_observations']={
        'encryption_command_seen':result['encryption'] is not None,
        'code_signature_command_seen':result['code_signature'] is not None,
        'ppl_status':'not_determinable_from_macho_header',
        'sptm_status':'not_determinable_from_macho_header',
        'note':'These fields require build-specific kernel/mitigation evidence; absence of a load command is not evidence that a mitigation is absent.'}
    return result

def analyze_ipsw(path: str | Path, board_id: int | None=None, chip_id: int | None=None, verify_zip: bool=False) -> dict[str, Any]:
    ipsw=Path(path)
    if not ipsw.is_file(): raise FileNotFoundError(f'IPSW not found: {ipsw}')
    with zipfile.ZipFile(ipsw,'r') as z:
        names=set(z.namelist())
        if 'BuildManifest.plist' not in names: raise ValueError('BuildManifest.plist is missing')
        manifest_bytes=z.read('BuildManifest.plist')
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest()
        manifest=plistlib.loads(manifest_bytes)
        bad_member=z.testzip() if verify_zip else None
        if not isinstance(manifest,dict): raise ValueError('BuildManifest.plist root is not a dictionary')
        product=_str(manifest.get('ProductVersion')); build=_str(manifest.get('ProductBuildVersion'))
        supported=manifest.get('SupportedProductTypes',[])
        if not isinstance(supported,list): supported=[]
        identities=_identity_records(manifest)
        matches=[]
        for ident in identities:
            checks={'product_type':TARGET_PRODUCT in [str(x) for x in supported],
                'device_class':ident['device_class']==TARGET_PRODUCT,
                'chip_id':chip_id is None or ident['ap_chip_id']==chip_id,
                'board_id':board_id is None or ident['ap_board_id']==board_id}
            ident['target_match_checks']=checks
            ident['matches_requested_hardware_ids']=all(checks.values())
            if ident['matches_requested_hardware_ids']: matches.append(ident)
        # Inspect only a small, explicit allowlist of manifest component files.
        inspections=[]
        for ident in matches[:8]:
            for comp in ident['components']:
                if comp['component'] not in ('KernelCache','iBoot','LLB') or not comp.get('path'): continue
                member=comp['path'].lstrip('/')
                # Reject archive traversal / absolute paths; never extract members.
                if member.startswith('../') or '/..' in member.split('/') or member.startswith('\\'):
                    inspections.append({'identity_index':ident['index'],'component':comp['component'],
                        'archive_path':member,'archive_member_present':False,
                        'macho_metadata':{'format':'not_inspected','reason':'unsafe_manifest_path'}})
                    continue
                if member not in names:
                    inspections.append({'identity_index':ident['index'],'component':comp['component'],
                        'archive_path':member,'archive_member_present':False,
                        'macho_metadata':{'format':'not_inspected','reason':'archive_member_missing'}})
                    continue
                try:
                    info=z.getinfo(member)
                    if info.file_size>128*1024*1024:
                        parsed={'format':'not_inspected','reason':'component_over_128MiB_limit','uncompressed_size':info.file_size}
                    else:
                        
                        with z.open(member, 'r') as stream:
                            parsed=_read_macho_header(stream.read(2*1024*1024))
                except (KeyError,RuntimeError,zipfile.BadZipFile) as exc:
                    parsed={'format':'not_inspected','reason':type(exc).__name__}
                inspections.append({'identity_index':ident['index'],'component':comp['component'],
                    'archive_path':member,'archive_member_present':True,'uncompressed_size':info.file_size,
                    'macho_metadata':parsed})
    exact=TARGET_PRODUCT in [str(x) for x in supported] and product=='27.0' and build==TARGET_BUILD
    return {'tool_version':VERSION,'input':{'filename':ipsw.name,'size_bytes':ipsw.stat().st_size},
        'firmware':{'product_version':product,'build_version':build,'supported_product_types':[str(x) for x in supported],
            'target_product_supported':TARGET_PRODUCT in [str(x) for x in supported]},
        'requested_hardware_ids':{'chip_id':chip_id,'board_id':board_id},
        'archive_integrity':{'crc_check_performed':verify_zip,'first_bad_member':bad_member,
            'status':'not_checked' if not verify_zip else ('failed' if bad_member else 'passed')},
        'manifest_sha256':manifest_sha256,
        'build_identities':identities,'matching_build_identity_indexes':[x['index'] for x in matches],
        'component_macho_inspections':inspections,
        'compatibility':{'exact_iphone12_27_0_24A437_match':exact,'full_jailbreak_proven':False,
            'note':'Static metadata is not vulnerability evidence and cannot establish a working exploit or Root chain.'},
        'analysis_limits':['Reads BuildManifest.plist and selected ZIP members only.','No decryption, decompression, disassembly, exploit execution, patching, restore, or device writes.','Compressed/encrypted kernel caches may not expose a plain Mach-O header.','A Mach-O header or UUID does not prove a vulnerability or exploitability.','PPL/SPTM state cannot be inferred from these Mach-O metadata fields.']}

def main() -> int:
    ap=argparse.ArgumentParser(description='Read-only IPSW manifest and Mach-O metadata analyzer')
    ap.add_argument('ipsw'); ap.add_argument('--json',action='store_true')
    ap.add_argument('--board-id',type=lambda x:int(x,0),help='Hardware board ID, e.g. 0x..')
    ap.add_argument('--chip-id',type=lambda x:int(x,0),help='Hardware chip ID, e.g. 0x8101')
    ap.add_argument('--verify-zip',action='store_true',help='Read all ZIP members to verify CRC (can take a long time)')
    ap.add_argument('--output',help='Write the JSON report to this path')
    a=ap.parse_args()
    try: r=analyze_ipsw(a.ipsw,a.board_id,a.chip_id,a.verify_zip)
    except (OSError,zipfile.BadZipFile,plistlib.InvalidFileException,ValueError) as e: ap.error(str(e))
    if a.output:
        Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if a.json: print(json.dumps(r,ensure_ascii=False,indent=2))
    else:
        f=r['firmware']; print(f"i12 Jailbreak Lab v{VERSION} — read-only IPSW analysis")
        print(f"Firmware: iOS {f['product_version']} ({f['build_version']})")
        print(f"Supports {TARGET_PRODUCT}: {f['target_product_supported']}")
        print(f"Matching BuildIdentity indexes: {r['matching_build_identity_indexes']}")
        print(f"Manifest SHA-256: {r['manifest_sha256']}")
        print(f"Archive CRC: {r['archive_integrity']['status']}")
        if a.output: print(f"JSON report written: {a.output}")
        for x in r['component_macho_inspections']:
            m=x['macho_metadata']; print(f"- {x['component']} [{x['archive_path']}]: {m.get('format')} {m.get('cpu_name','')}")
        print('Static metadata only; this is NOT a jailbreak or exploit test.')
    return 0
if __name__=='__main__': raise SystemExit(main())
