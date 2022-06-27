#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void)
{
    long a;
    long b = 100;
    long c = 0;
    int d = 0;

    do
    {
        printf("C = %li \n", c);

        a = get_long("Number: ");

    }
    while (a < 1);
    
    if (a < 4000000000000 || a > 5600000000000000)
    {
        d++;
    }

    long e = round((a % b) / (b / 10));

    while (b <= 10000000000000000)
    {
        e = round((a % b) / (b / 10));

        c = c + (e * 2 % 10) + (round((e * 2 % 100) / 10));

        b = b * 100;
    }

    b = 10;

    while (b <= 1000000000000000)
    {
        c = c + (round((a % b) / (b / 10)));

        b = b * 100;
    }

    if (c % 10 != 0 || c < 1 || d >= 1)
    {
        printf("INVALID\n");
    }
    
    else if ((c % 10 == 0) && (((round(a / 10000000000000)) <= 559) && ((round(a / 10000000000000)) >= 510)))
    {
        printf("MASTERCARD\n");
    } 
    
    else if ((c % 10 == 0) && (((round(a / 1000000000000)) <= 379) && ((round(a / 1000000000000)) >= 340) && ((round(a / 10000000000000)) != 35) && ((round(a / 10000000000000)) != 36)))
    {
        printf("AMEX\n");
    } 
    
    else if ((c % 10 == 0) && (((round(a / 1000000000000)) == 4) || ((round(a / 1000000000000000)) == 4)))
    {
        printf("VISA\n");
    } 
    
    else
    {
        printf("INVALID\n");
    }
    
}
