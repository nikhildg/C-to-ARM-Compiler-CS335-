    using System;
    namespace check1

    {

        class Program

        {

            int Main()

            {
                int i;
                i = -6;
                int a = 0;
                Console.WriteLine("{0}",i);
                if(i%2==0){
                    a = 0;
                    Console.WriteLine("{0}",a);
                    if(a == 0){
                        Console.WriteLine("{0}",-100);
                    }
                    else{
                        Console.WriteLine("{0}",-100);
                    }
                }
                else{
                    Console.WriteLine("{0}",1);
                    a = 1;
                    if(a == 0){
                        Console.WriteLine("{0}",100);
                    }
                    else{
                        Console.WriteLine("{0}",-100);
                    }
                }
                Console.WriteLine("{0}",2);
                return 0;
            }

        }

    }
