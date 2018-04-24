using System;
namespace palindrome
{
    class Program
    {
        static int Main(string[] args)
        {
            int i,j,k,res;
            for(res = 0, i=0; i < 10; i++){
                for(j = 0; j < 10; j++){
                    for(k = 0; k < 10; k++){
                        res += 1;
                    }
                }
            }
            Console.WriteLine("res = {0}\n", res);
            return 0;
        }
    }
}

