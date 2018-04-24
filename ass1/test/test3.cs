/*
 * C# Program to calculate factorial of a number
 */
using System;
 
class FindFactorial
{
    static void Main()
    {
        Console.WriteLine("Enter number: ");
        int num = int.Parse(Console.ReadLine());
        int fact = 1;
        for (int i = 1; i <= num; i++)
        {
            fact *= i;
        }
 
        Console.WriteLine(fact);
    }
}
