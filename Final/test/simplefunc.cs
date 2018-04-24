using System;
namespace Program
{
    class Program
    {

        int hey(){
            return 2; 
        }
        void haha(){
            int x = -22;
            int y =2; 
            int z = hey();
            Console.WriteLine("{0}",y);
            Console.WriteLine("{0}",x);
            return;
        }
        int Main()
        { 
            int a = 12;
            if(a<13)
            {
                int j=0;
                Console.WriteLine("{0}",j);
            }
            int y = 2;
            haha();
            int x = 2;
            Console.WriteLine("{0}",y);
            Console.WriteLine("{0}",x);
            return 0;
        }
    }
}