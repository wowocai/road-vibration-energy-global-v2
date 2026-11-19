import ctypes as C,ctypes.util
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'fonts';L=C.CDLL(ctypes.util.find_library('archive'))
L.archive_read_new.restype=C.c_void_p
L.archive_read_support_format_all.argtypes=[C.c_void_p];L.archive_read_support_filter_all.argtypes=[C.c_void_p]
L.archive_read_open_filename.argtypes=[C.c_void_p,C.c_char_p,C.c_size_t]
L.archive_read_next_header.argtypes=[C.c_void_p,C.POINTER(C.c_void_p)]
L.archive_entry_pathname.argtypes=[C.c_void_p];L.archive_entry_pathname.restype=C.c_char_p
L.archive_entry_size.argtypes=[C.c_void_p];L.archive_entry_size.restype=C.c_longlong
L.archive_read_data.argtypes=[C.c_void_p,C.c_void_p,C.c_size_t];L.archive_read_data.restype=C.c_ssize_t
L.archive_read_free.argtypes=[C.c_void_p]
a=L.archive_read_new();L.archive_read_support_format_all(a);L.archive_read_support_filter_all(a)
assert L.archive_read_open_filename(a,str(P/'times32.cab').encode(),10240)==0
ent=C.c_void_p()
while L.archive_read_next_header(a,C.byref(ent))==0:
 name=L.archive_entry_pathname(ent).decode();size=L.archive_entry_size(ent);buf=C.create_string_buffer(size);n=L.archive_read_data(a,buf,size)
 if name.lower().endswith(('.ttf','.txt')):
  path=P/Path(name).name;path.write_bytes(buf.raw[:n]);print(path.name,n)
L.archive_read_free(a)
from fontTools.ttLib import TTFont
for f in P.glob('*.ttf'):
 font=TTFont(f);print(f.name,[n.toUnicode() for n in font['name'].names if n.nameID==1][:1])
