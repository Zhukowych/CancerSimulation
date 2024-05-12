
# Cancer simulation
We implemented cancer development and chemotherapy impact simulation using **stochastic cellular automaton** with Python

# Instalation
To use app you must clone it from git repo and install requirements. Preferrable version Python3.12
```
git clone https://github.com/Zhukowych/CancerSimulation.git
cd CancerSimulation
pip install -r requirements
```

# Model
In this project we implemented models proposed in the following articles. First focus on main principles of cancer growth, while second introduces main principles of chemotherapy treatment simulation.
- [Cellular-automaton model for tumor growth dynamics: Virtualization of different scenarios](https://www.sciencedirect.com/science/article/pii/S0010482522011891?ref=pdf_download&fr=RR-2&rr=8800d112bd3635b1)
- [A cellular automata model of chemotherapy effects on tumour growth: targeting cancer and immune cells](https://www.tandfonline.com/doi/full/10.1080/13873954.2019.1571515)


By combining models from both articles we have have following states and, list of initial parameters and set of rules:


#### States (Table 1)
| State Index | Description | Abbreviation |
| --- | ---| --- |
| 0   | Empty Cell | EC
| 1   | Regular cancer cell | RTC
| 2   | Stem Cell | SC
| 3   | Quiescent Cell | QC
| 4   | Necrotic Cell | NC
| 5   | Immune Cell | IC 

#### Initial parameters (Table 2)


| Parameter | Description | Name in config file | Default value |
| --- | ---| --- |--- |
| $p_0$   | Probability of division | | 0.7
| $p_S$   | Probability of stem division | | 0.1
| $p_A$   | Probability of apotosis (spontaneous death) | | 0.3
| $\mu$  | Migration probability | | 0.4
| $R_{max}$   | Maximum tumor extent | | 37.5
| $p_{dT}$   | Tumor death constant | | 37.5
| $p_{I}$   | Immune death constant | | 37.5
| $K_{c}$   | Chemotherapy effect on division | | 37.5
| $y_{PC}$   | PC's resistance to treatment | | 37.5
| $y_{Q}$   | QC's resistance to treatment | | 37.5
| $y_{I}$   | IC's resistance to treatment | | 37.5
| $k_{PC}$   | PC's death due to treatment | | 37.5
| $k_{Q}$   | QC's death due to treatment | | 37.5
| $k_{I}$   | IC's death due to treatment | | 37.5
| $c_{i}$   | The attenuation coefficient of a drug for any cell type | | 37.5
| $n_{dead}$ | Number of steps before death due to treatment | | 4 |
| $PK$   | Pharmacokinetics | | 37.5
| $t_{ap}$   | Start time of therapy | | -
| $t_{per}$   | Time interval between injections | | -
| $\tau$   | time constant of each dose | | 

### Transition rules

Simulation starts with cancer cell at the center of the lattice. Then the following rules are applied to each active (non-empty) cell.

#### Growth rules
- RTC can undergo apotosis (spontaneous cell death) with probability $p_A$. SC cannot spontaneously die due to this
- A RTC and SC cells can **proliferate** (divide) with probability $br$ if there is empty neighbor cell. Probability depends on distance from the center of the tumor and parameters $R_{max}$ and $K_c$. $R_{max}$ is used to factor in the pressure of surrounding tissue and $K_c$ to take into account maximum possible population of cancer cells in environment. 
$$br = p_0 \left(1 - \frac{r}{R_{max} - K_c}\right) $$
 - While RTC and SC proliferate with same probability, they have differences. Each RTC has finite number of possible proliferations given with parameter **max_proliferation_potential**, and with each division this potential decreases by one. When potential is 0, cell dies. SC can proliferate infinitely, but it has probability $p_S$ of dividing into two stem cells, otherwise it will proliferate into two RTCs with maximum_proliferation potential
 - RTC and SC can migrate to free neighbor cell with probability $\mu$
 - If RTC or SC are **necrotic_distance** from cancer edges, they became necrotic cells (NC), which cannot be affected neither by immune system nor by chemotherapy.
 - ICs walk randomly on the lattice, but generally move to the center of the tumor. If IC meets RTC or SC, then following actions will happen:
    1. Cancer cell will die with probability $p_{dT}$ 
    2. IC will die with probability $p_{dI}$, the RTC or SC will remain alive
    3. IC will continue random walk while another RTC or SC will not be found
    4. New ICs will be recruited according to the following law, where nIC, nRTC, nT - is number of ICs, RTCs and total number of tumor cells in current iteration. $\rho$ is the recruiting coefficient. Also we can set the limit of ICs by **max_immune_cell_count** parameter
    $$R = \rho\frac{nIC(t)\times nRTC(t)}{10^3 + nT(t)}$$

#### Therapy impact

Firstly, we must make several assumptions:
- Cancer cells can be divided into two types: drug-resistant cells (SC) and drug-sensitive cells (RTC). 
- Drug is evenly distributed among all cells
- We can affect tumor growth via reducing probability of proliferation, increasing probability of cell death and decreasing $K_c$

Drug can kill RTC, QC, IC with different probabilities:

$$F_i(g) = l_i\times PK\times e^{-c_i(t - n_d\tau)}$$

$$l_i=\frac{l_i\times g}{y'_i\times n_d+1}$$

$$y'_i = \theta\times y_i$$ 

$$ 0<random \theta \leq1$$

where i can be (RTC, QC, IC) and $g$ is the drug concentration at each cell. Also therapy affects proliferation potentiaд

$$p_0' = \frac{p_0\times y_{PC}}{n_d^{1/n_{dead}}}$$


Therapy is applied from $t_{ap}$ day with $t_{per}$ intervals and drug concentration remain the same during $\tau$ days after the injection