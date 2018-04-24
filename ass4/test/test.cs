using System;
namespace Program {
    class D{
        int n;
        int arr=0;
        void setD()
        {
            n = 10;
            int i;
            for(i=0;i<n;i++)
            {
                arr  = -n -i;
            }
        }
    }
    class A{
        int Main()
        {
            D temp = new D();
            temp.setD();
            return 0;
        }
    }
}