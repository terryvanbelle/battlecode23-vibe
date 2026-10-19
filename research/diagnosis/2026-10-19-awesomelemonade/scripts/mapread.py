import struct, os, functools
MAPDIR='/home/terryvanbelle/projects/vibe/reference/battlecode23/engine/src/main/battlecode/world/resources'
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
@functools.lru_cache(None)
def load(name):
    b=open(os.path.join(MAPDIR,name+'.map23'),'rb').read()
    t=u32(b,0)
    vt=t-i32(b,t)
    vlen=u16(b,vt)
    def fo(i):
        p=vt+4+2*i
        if p>=vt+vlen: return 0
        return u16(b,p)
    def vec(i,sz,fmt):
        o=fo(i)
        if not o: return []
        p=t+o; p+=u32(b,p); n=u32(b,p); p+=4
        return list(struct.unpack_from('<%d%s'%(n,fmt),b,p))
    mn=t+fo(1); mx=t+fo(2)
    x0,y0=i32(b,mn),i32(b,mn+4); x1,y1=i32(b,mx),i32(b,mx+4)
    W,H=x1-x0,y1-y0
    walls=vec(6,1,'B'); clouds=vec(7,1,'B'); isl=vec(9,4,'i')
    return dict(W=W,H=H,walls=walls,clouds=clouds,islands=isl)
def island_tiles(name):
    m=load(name); W=m['W']; d={}
    for k,v in enumerate(m['islands']):
        if v>0: d.setdefault(v,[]).append((k%W,k//W))
    return d
if __name__=='__main__':
    import sys
    for n in sys.argv[1:]:
        m=load(n); it=island_tiles(n)
        print(n,m['W'],m['H'],len(m['walls']),sum(m['walls']),sum(m['clouds']),{k:len(v) for k,v in it.items()})
