/*
 * C# Program to Check whether the Entered Number is Even or Odd
 */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
 
namespace test1
{
    class Program
    {
        static void Main(string[] args)
        {
            int num;//Enter a number
            num = int.Parse(Console.ReadLine());
            if (num % 2 == 0)
            {
                Console.Write("The number is even");
            }
            else
            {
                Console.Write("The number is Odd");
            }
        }
    }
}
