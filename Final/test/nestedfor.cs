using System;
namespace Program
{
    class Program
    {
        int Main()
        { 
            int a = 12;
            int i=0;
            int j =0;
            int a1=1;
            int a2=1;
            int a3=1;
            int a4=1;
            int a5=1;
            for (i = 8; i <= a; i++)
            {

                Console.WriteLine("{0}",i);
                for (i = 10; i <= a; i++)
                {
                    Console.WriteLine("{0}",i);
                    Console.WriteLine("{0}",a);
                }

            }
            Console.WriteLine("{0}",a);
            return 0;
        }
    }
}

