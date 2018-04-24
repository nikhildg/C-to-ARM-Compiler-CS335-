/*
 * C# Program to Get a Number and Display the Sum of the Digits 
 */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
 
namespace Program
{
    class Program
    {
        static void Main(string[] args)
        {
            int dig`it, sum = 0, temp;           //digit is 'invalid token' 
            Console.WriteLine("Enter number : ");
            digit = int.Parse(Console.ReadLine());
            for(;digit!=0;)
            {
                temp = dig`it % 10;          //Invalid token `
                digit = dig$it / 10;           //Invalid token $
                sum = sum + temp;
            }
            Console.WriteLine("Sum of Digits : "+sum);   //Inserting invalid double quotes!
 
        }
    }
}
