import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.nio.file.*;
import java.util.*;

/** Compare existing executable methods after package normalization; ignore debug metadata and unused additions. */
public final class BytecodeIdentity {
    static String norm(Object v){return String.valueOf(v).replace("c_mend2/","PKG/").replace("c_explore0/","PKG/").replace("c_mend2.","PKG.").replace("c_explore0.","PKG.");}
    static Map<String,String> methods(Path file)throws Exception {
        ClassNode c=new ClassNode();new ClassReader(Files.readAllBytes(file)).accept(c,ClassReader.SKIP_DEBUG|ClassReader.SKIP_FRAMES);
        Map<String,String> result=new TreeMap<>();
        for(Object obj:c.methods){MethodNode m=(MethodNode)obj;Map<LabelNode,Integer> labels=new IdentityHashMap<>();int pos=0;
            for(AbstractInsnNode n=m.instructions.getFirst();n!=null;n=n.getNext()){if(n instanceof LabelNode)labels.put((LabelNode)n,pos);else if(n.getOpcode()>=0)pos++;}
            StringBuilder code=new StringBuilder().append(m.access).append('|').append(norm(m.desc)).append('|');
            for(AbstractInsnNode n=m.instructions.getFirst();n!=null;n=n.getNext()){
                if(n.getOpcode()<0)continue;code.append(n.getOpcode()).append(':');
                if(n instanceof VarInsnNode)code.append(((VarInsnNode)n).var);
                else if(n instanceof IntInsnNode)code.append(((IntInsnNode)n).operand);
                else if(n instanceof TypeInsnNode)code.append(norm(((TypeInsnNode)n).desc));
                else if(n instanceof FieldInsnNode){FieldInsnNode f=(FieldInsnNode)n;code.append(norm(f.owner)).append('.').append(f.name).append(norm(f.desc));}
                else if(n instanceof MethodInsnNode){MethodInsnNode f=(MethodInsnNode)n;code.append(norm(f.owner)).append('.').append(f.name).append(norm(f.desc)).append(f.itf);}
                else if(n instanceof InvokeDynamicInsnNode){InvokeDynamicInsnNode d=(InvokeDynamicInsnNode)n;code.append(d.name).append(norm(d.desc)).append(norm(d.bsm)).append(norm(Arrays.toString(d.bsmArgs)));}
                else if(n instanceof JumpInsnNode)code.append(labels.get(((JumpInsnNode)n).label));
                else if(n instanceof LdcInsnNode)code.append(norm(((LdcInsnNode)n).cst));
                else if(n instanceof IincInsnNode){IincInsnNode x=(IincInsnNode)n;code.append(x.var).append(',').append(x.incr);}
                else if(n instanceof TableSwitchInsnNode){TableSwitchInsnNode s=(TableSwitchInsnNode)n;code.append(s.min).append(',').append(s.max).append(',').append(labels.get(s.dflt));for(Object label:s.labels)code.append(',').append(labels.get((LabelNode)label));}
                else if(n instanceof LookupSwitchInsnNode){LookupSwitchInsnNode s=(LookupSwitchInsnNode)n;code.append(s.keys).append(',').append(labels.get(s.dflt));for(Object label:s.labels)code.append(',').append(labels.get((LabelNode)label));}
                else if(n instanceof MultiANewArrayInsnNode){MultiANewArrayInsnNode x=(MultiANewArrayInsnNode)n;code.append(norm(x.desc)).append(',').append(x.dims);}
                code.append(';');
            }
            for(Object x:m.tryCatchBlocks){TryCatchBlockNode t=(TryCatchBlockNode)x;code.append("catch:").append(labels.get(t.start)).append(',').append(labels.get(t.end)).append(',').append(labels.get(t.handler)).append(',').append(norm(t.type)).append(';');}
            result.put(m.name+norm(m.desc),code.toString());
        }return result;
    }
    public static void main(String[] args)throws Exception {
        Path root=Paths.get(args[0]);int classes=0,methods=0;
        try(DirectoryStream<Path> stream=Files.newDirectoryStream(root.resolve("c_mend2"),"*.class")) {
            for(Path base:stream){Map<String,String> a=methods(base),b=methods(root.resolve("c_explore0").resolve(base.getFileName()));classes++;
                for(Map.Entry<String,String> entry:a.entrySet()){methods++;if(!entry.getValue().equals(b.get(entry.getKey())))throw new AssertionError("zero-arm executable bytecode differs: "+base.getFileName()+" "+entry.getKey());}
            }
        }
        System.out.println("{\"zero_arm_existing_method_identity\":true,\"classes\":"+classes+",\"methods\":"+methods+",\"normalization\":\"package/debug metadata; additional unreachable helper methods/unused fields excluded\"}");
    }
}
