## Horodecki Measure

Like mentioned in the [`README.md`](README.md) for the repository we can represent the CHSH inequality in diffrent ways. For the Horodecki measure we take the method of the CHSH operator $\mathcal{B}_{CHSH}$. Again we define the coorlation matrix as $T_{i,j} = \text{Tr} \left[\rho \left(\sigma_i \otimes \sigma_j \right)\right]$. 

And the max possible value for the CHSH operatior given the density matrix $\rho$ is

$$\max_{\mathcal{B}_{CHSH}}{|\text{Tr}(\rho \mathcal{B}_{CHSH})|} = 2 \sqrt{\mathcal{M}(\rho)}$$

where $\mathcal{M}(\rho) = \max_{i > j}{(u_i +u_j)}$ where $u_i$ are eigenvalues of $T^\dagger T$. And in this represenation the CHSH inequality is only violated iff $\mathcal{M}(\rho) > 1$. We then can define

$$B(\rho) \equiv \sqrt{\mathcal{M}(\rho) - 1}$$ 

Some may also say:

$$B(\rho) \equiv \sqrt{\max[0, \mathcal{M}(\rho) - 1]}$$ 

just so that the $B$ remains a real value function and we call it the Horodecki measure of the CHSH inequlaity. Its values range from $0$ to $1$ with larger meaning more entangled.
