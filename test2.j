.source                  test2.java
.class                   public test2
.super                   java/lang/Object
   
.field                   public static SCANER Ljava/util/Scanner;
.field                   public static a I
.field                   public static ar [I
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

.method                  public static func([I)V
   .limit stack          10
   .limit locals         4
   iconst_0
   istore                1
   iconst_1
   istore                2
   ldc                   1
   istore                3
   ldc                   1
   istore                3
LABEL_7:
   iload                 3
   ldc                   10
   if_icmpgt             LABEL_8
   aload                 0
   iload                 3
   ldc                   1
   isub
   iaload
   ldc                   0
   if_icmpne             LABEL_12
   iconst_1
   goto                  LABEL_13
LABEL_12:
   iconst_0
LABEL_13:
   ifeq                  LABEL_9
   iload                 1
   ifeq                  LABEL_14
   return
   goto                  LABEL_15
LABEL_14:
LABEL_15:
   iconst_1
   istore                1
   goto                  LABEL_10
LABEL_9:
   iload                 1
   ifeq                  LABEL_16
   getstatic             java/lang/System/out Ljava/io/PrintStream;
   new                   java/lang/StringBuilder
   dup
   invokespecial         java/lang/StringBuilder/<init>()V
   ldc                   "\n"
   invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;
   aload                 0
   iload                 3
   ldc                   1
   isub
   iaload
   invokestatic          java/lang/String/valueOf(I)Ljava/lang/String;
   invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;
   invokevirtual         java/lang/StringBuilder/toString()Ljava/lang/String;
   invokevirtual         java/io/PrintStream/print(Ljava/lang/String;)V
   goto                  LABEL_17
LABEL_16:
LABEL_17:
LABEL_10:
   iload                 3
   iconst_1
   iadd
   istore                3
   goto                  LABEL_7
LABEL_8:
   return
.end method
   
.method                  public static main([Ljava/lang/String;)V
   .limit stack          10
   .limit locals         1
   ldc                   0
   putstatic             test2/a I
   ldc                   10
   newarray              int
   putstatic             test2/ar [I
   ldc                   1
   putstatic             test2/i I
LABEL_18:
   getstatic             test2/i I
   ldc                   10
   if_icmpgt             LABEL_19
   getstatic             test2/SCANER Ljava/util/Scanner;
   invokevirtual         java/util/Scanner/nextInt()I
   putstatic             test2/a I
   getstatic             test2/ar [I
   getstatic             test2/i I
   ldc                   1
   isub
   getstatic             test2/a I
   iastore
   getstatic             test2/i I
   iconst_1
   iadd
   putstatic             test2/i I
   goto                  LABEL_18
LABEL_19:
   getstatic             test2/ar [I
   invokestatic          test2/func([I)V
   getstatic             test2/SCANER Ljava/util/Scanner;
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
   putstatic             test2/SCANER Ljava/util/Scanner;
   return
.end method

   
