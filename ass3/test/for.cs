using System;
namespace palindrome
{
    class Program
    {
        static int Main(string[] args)
        {
            int i=6;
            for (;i<= 8 && i>= 6 && i!= 7; i++){
                if (i>=0){
                    Console.WriteLine("yes\n");
                }
                else 
                    Console.WriteLine("no\n");
            }
            return 0;
        }
    }
}

