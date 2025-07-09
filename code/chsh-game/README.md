## Classic CHSH Game
The code in this folder is for a classical CHSH game between Alice and Bob. 

![alt text](image.png)
In the code example alice is one qubit and bob is another. The goal of the game is to fullfil the equality $$x \wedge y = a \oplus b$$given $x, y$ which are either $1$ or $0$ and Alice and Bob respond with $a, b$. XOR (or $\oplus$) returns $1$ if one of its inputs is $1$ and logical AND ($\wedge$) returns $1$ when both inputs are the same.

With classical techinquies this is only winable up to 75% of the time, but with quantum techinques we can win up to about 85% of the time (given by Tsirelson’s bound).

The ciruit I implent sets up Alice and Bob in a bell state (specifically $|\phi_0\rangle = \frac{1}{\sqrt2}(|00\rangle + |11\rangle$) and then proceds to change the measurment basis depending on the given $x, y$. If `x == 0` then Alice measures in the normal Z-basis and if `x == 1` then she measures in the X-basis (hence the applicaiton of the Hadamard). If `x == 0` then Bob measures in the $\frac{Z + X}{\sqrt2}$ basis and if `x == 1` then she measures in the $\frac{Z - X}{\sqrt2}$ basis.

I'll add more documentation explaing how it works.