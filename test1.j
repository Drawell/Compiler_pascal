.source                  tmp.java
.class                   public tmp
.super                   java/lang/Object
   
.field                   public static SCANER Ljava/util/Scanner;
.field                   public static a I
.field                   public static s Ljava/lang/String;
.field                   public static as [Ljava/lang/String;
.field                   public static i I
   
.method                  public <init>()V
   .limit stack          1
   .limit locals         1
   aload_0
   invokespecial         java/lang/Object/<init>()V
   return
.end method
   
.method                  public static toBoolean(I)Z
   .limit stack          1
   .limit locals         1
   iload_0
   ifeq                  LABEL1
   iconst_1
   goto                  LABEL2
LABEL1:
   iconst_0              
LABEL2:
   ireturn               
.end method

.method                  public static toBoolean(F)Z
   .limit stack          2
   .limit locals         1
   fload_0
   fconst_0
   fcmpl
   ifeq                  LABEL3
   iconst_1
   goto                  LABEL4
LABEL3:
   iconst_0
LABEL4:
   ireturn
.end method

.method                  public static toBoolean(Ljava/lang/String;)Z
   .limit stack          2
   .limit locals         1
   aload_0
   ldc                   ""
   if_acmpeq             LABEL5
   iconst_1
   goto                  LABEL6
LABEL5:
   iconst_0 
LABEL6:
   ireturn
.end method

.method                  public static sort_str([Ljava/lang/String;)V
   .limit stack          10
   .limit locals         4
   iconst_1
   istore                1
LABEL_7:
   iload                 1
   ifeq                  LABEL_8
   iconst_0
   istore                1
   ldc                   1
   istore                2
LABEL_9:
   iload                 2
   ldc                   4
   if_icmpgt             LABEL_10
   aload                 0
   iload                 2
   ldc                   1
   isub
   aaload
   invokevirtual         java/lang/String/length()I
   aload                 0
   iload                 2
   ldc                   1
   iadd
   ldc                   1
   isub
   aaload
   invokevirtual         java/lang/String/length()I
   if_icmpge             LABEL_14
   iconst_1
   goto                  LABEL_15
LABEL_14:
   iconst_0
LABEL_15:
   ifeq                  LABEL_11
   aload                 0
   iload                 2
   ldc                   1
   isub
   aaload
   astore                3
   aload                 0
   iload                 2
   ldc                   1
   isub
   aload                 0
   iload                 2
   ldc                   1
   iadd
   ldc                   1
   isub
   aaload
   aastore
   aload                 0
   iload                 2
   ldc                   1
   iadd
   ldc                   1
   isub
   aload                 3
   aastore
   iconst_1
   istore                1
   goto                  LABEL_12
LABEL_11:
LABEL_12:
   iload                 2
   iconst_1
   iadd
   istore                2
   goto                  LABEL_9
LABEL_10:
   goto                  LABEL_7
LABEL_8:
   return
.end method
   
.method                  public static main([Ljava/lang/String;)V
   .limit stack          10
   .limit locals         1
   ldc                   0
   putstatic             tmp/a I
   ldc                   "hi"
   putstatic             tmp/s Ljava/lang/String;
   ldc                   5
   anewarray              java/lang/String
   putstatic             tmp/as [Ljava/lang/String;
   ldc                   1
   putstatic             tmp/i I
LABEL_16:
   getstatic             tmp/i I
   ldc                   5
   if_icmpgt             LABEL_17
   getstatic             tmp/SCANER Ljava/util/Scanner;
   invokevirtual         java/util/Scanner/next()Ljava/lang/String;
   putstatic             tmp/s Ljava/lang/String;
   getstatic             tmp/as [Ljava/lang/String;
   getstatic             tmp/i I
   ldc                   1
   isub
   getstatic             tmp/s Ljava/lang/String;
   aastore
   getstatic             tmp/i I
   iconst_1
   iadd
   putstatic             tmp/i I
   goto                  LABEL_16
LABEL_17:
   getstatic             tmp/as [Ljava/lang/String;
   invokestatic          tmp/sort_str([Ljava/lang/String;)V
   ldc                   1
   putstatic             tmp/i I
LABEL_18:
   getstatic             tmp/i I
   ldc                   5
   if_icmpgt             LABEL_19
   getstatic             java/lang/System/out Ljava/io/PrintStream;
   new                   java/lang/StringBuilder
   dup
   invokespecial         java/lang/StringBuilder/<init>()V
   ldc                   "\n"
   invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;
   getstatic             tmp/as [Ljava/lang/String;
   getstatic             tmp/i I
   ldc                   1
   isub
   aaload
   invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;
   invokevirtual         java/lang/StringBuilder/toString()Ljava/lang/String;
   invokevirtual         java/io/PrintStream/print(Ljava/lang/String;)V
   getstatic             tmp/i I
   iconst_1
   iadd
   putstatic             tmp/i I
   goto                  LABEL_18
LABEL_19:
   getstatic             tmp/SCANER Ljava/util/Scanner;
   invokevirtual         java/util/Scanner/close()V
   return
.end method
   
.method                  static <clinit>()V
   .limit stack          10
   .limit locals         0
   new                   java/util/Scanner
   dup
   getstatic             java/lang/System/in Ljava/io/InputStream;
   invokespecial         java/util/Scanner/<init>(Ljava/io/InputStream;)V
   putstatic             tmp/SCANER Ljava/util/Scanner;
   return
.end method

   
