/*
   Name: A J Hacker
   Section: 99966532
   Assignment: 00
   Due: August 26, 1990
   Credit: 15 points.

   Problem: There is some problem description here.
   Solution: The solution of the problem goes here.
   Errors handled: Any errors that are handled goes here.
   Limitations: Limitations of the program/algorithm/etc. go here.
   Acknowledgement: Acknoledgement of help goes here.
*/

#include <stdio.h>
#include <stdlib.h>

#define A_DEFINITION 500

struct somestruct {
   int avalue;
   char anothervalue;
};
typedef struct somestruct somestruct;

int aglobal;


/* Description of the main function occurs in this comment block.  The comment
   has a manual break line. */
int main(int argc, char *argv[])
{
   int customfunction(char);
   void srandom(unsigned int);
   time_t time(time_t *);

   time_t * mytime;
   char somelatervariable;

   customfunction(somelatervariable);
}


/* Description of the custom function.  There should be no comments within
   the function itself. */
int customfunction(char c)
{
   void dosomethingwithc(char *);

   int i = 0;
   for (i = 0; i < 100; i++)
   {
      dosomethingwithc(&c);
   }

   if (c == 'a')
      return true;
   else
      return false;
}


/* Description of second function prototyped in first. */
void dosomethingwithc(char *c)
{
   *c = *c + (char) 1;
}
