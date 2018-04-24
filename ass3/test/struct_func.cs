using System;
namespace palindrome
{
    struct T
    {
      public char a;
      public int b;
      public char c;
      public short d;
      public double e;
      public string name;
      public char f;

    }
    class Program
    {
        static void f (T x)
        {
          x.a = 'a';
          x.b = 47114711;
          x.c = 'c';
          x.d = 1234;
          x.e = 3.141592897932;
          x.f = '*';
          x.name = "abc";
        }
        static int Main(string[] args)
        {   
            T k;
            k=new T();
            f(k);
            return 0;
        }
    }
}
