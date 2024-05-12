
# Cancer simulation
We implemented cancer development and chemotherapy impact simulation using **stochastic cellular automaton** with Python. The main feature of implemented app is capability of simulating different treatment strategies under same-type cancer behavior.

![Alt text](img/first_screen.png?raw=true "Optional Title")

## Contents
- [Instalation](#instalation)
- [Usage](#usage)
- [Simulation model](#simulation-model)
    - [States](#states)
    - [Initial parameters](#initial-parameters)
    - [Transition rules](#transition-rules)
        - [Growth rules](#growth-rules)
        - [Therapy impact](#therapy-impact)
- [Implementation & architecture](#implementation--architecture)
    - [Model architecture](#model-architecture)
    - [GUI](#gui)
    - [Config file](#config-file)


## Instalation
To use app you must clone it from git repo and install requirements. Preferrable version Python3.12
```
git clone https://github.com/Zhukowych/CancerSimulation.git
cd CancerSimulation
pip install -r requirements
```

## Usage

To run app you must use the following bash command
```
python csimulation.py config.yaml
```
providing config.yaml file, which structure will be discussed further in the part [Config file](#config-file)

## Simulation model
In this project we implemented models proposed in the following articles. First focus on main principles of cancer growth, while second introduces main principles of chemotherapy treatment simulation.
- [Cellular-automaton model for tumor growth dynamics: Virtualization of different scenarios](https://www.sciencedirect.com/science/article/pii/S0010482522011891?ref=pdf_download&fr=RR-2&rr=8800d112bd3635b1)
- [A cellular automata model of chemotherapy effects on tumour growth: targeting cancer and immune cells](https://www.tandfonline.com/doi/full/10.1080/13873954.2019.1571515)


By combining models from both articles we have have following states and, list of initial parameters and set of rules:


### States
| State Index | Description | Abbreviation |
| --- | ---| --- |
| 0   | Empty Cell | EC
| 1   | Regular tumor cell | RTC
| 2   | Stem Cell | SC
| 3   | Quiescent Cell | QC
| 4   | Necrotic Cell | NC
| 5   | Immune Cell | IC 

### Initial parameters

| Parameter | Description | Name in config file | Default value |
| --- | ---| --- |--- |
| $p_0$   | Probability of division | p0 | 0.7
| $p_S$   | Probability of stem division | pS | 0.1
| $p_A$   | Probability of apotosis (spontaneous death) | pA | 0.01
| $\mu$  | Migration probability | mu | 0.4
| $R_{max}$   | Maximum tumor extent | Rmax | 37.5
| $p_{dT}$   | Tumor death constant | pdT | 0.5
| $p_{I}$   | Immune death constant | pdI | 0.2
| $K_{c}$   | Chemotherapy effect on division | Kc | $0 - R_{max}/2$
| $y_{PC}$   | PC's resistance to treatment | yPC | 0.55 - 0.95
| $y_{Q}$   | QC's resistance to treatment | yQ | 0 - 0.4
| $y_{I}$   | IC's resistance to treatment | yI | 0 - 0.7
| $k_{PC}$   | PC's death due to treatment | kPC | 0.8
| $k_{Q}$   | QC's death due to treatment | kQ | 0.4
| $k_{I}$   | IC's death due to treatment | kI | 0.6
| $c_{i}$   | The attenuation coefficient of a drug for any cell type | ci | 0.5 - 1
| $ics$   | How quickly IC will find tumor | ics | 0 - 1
| $icc$   | Immune cell concentration | icc | 0 - 10000
| $d_{QC}$ | Quiescent distance | quiescent_distance | - |
| $d_{NC}$ | Necrotic distance | necrotic_distance | - |
| $n_{dead}$ | Number of steps before death due to treatment | ndead | 4 |
| $PK$   | Pharmacokinetics | PK | 1
| $t_{ap}$   | Start time of therapy | treatment_start_time | -
| $t_{per}$   | Time interval between injections | injection_interval | -
| $\tau$   | time constant of each dose | time_constant | -
| $g$   | Drug concentration | g | -

### Transition rules

Simulation starts with cancer cell at the center of the lattice. Then the following rules are applied to each active (non-empty) cell.

### Growth rules
- RTC can undergo apotosis (spontaneous cell death) with probability $p_A$. SC cannot spontaneously die due to this
- A RTC and SC are both Proliferating cells that can **proliferate** (divide) with probability $br$ if there is empty neighbor cell. Probability depends on distance from the center of the tumor and parameters $R_{max}$ and $K_c$. $R_{max}$ is used to factor in the pressure of surrounding tissue and $K_c$ to take into account maximum possible population of cancer cells in environment. 
$$br = p_0 \left(1 - \frac{r}{R_{max} - K_c}\right) $$
 - While RTC and SC proliferate with same probability, they have differences. Each RTC has finite number of possible proliferations given with parameter **max_proliferation_potential**, and with each division this potential decreases by one. When potential is 0, cell dies. SC can proliferate infinitely, but it has probability $p_S$ of dividing into two stem cells, otherwise it will proliferate into two RTCs with maximum_proliferation potential
 - RTC and SC can migrate to free neighbor cell with probability $\mu$
 - If RTC or SC are **quiescent_distance** from tumor edges, it will turn to QC (quiescent cell). If QC is less that **quiescent_distance** from tumor edges, it will turn back to RTC or SC.
 - If RTC or SC are **necrotic_distance** from cancer edges, they became necrotic cells (NC), which cannot be affected neither by immune system nor by chemotherapy.
 - ICs walk randomly on the lattice, but generally move to the center of the tumor. If IC meets RTC or SC, then following actions will happen:
    1. Cancer cell will die with probability $p_{dT}$ 
    2. IC will die with probability $p_{dI}$, the RTC or SC will remain alive
    3. IC will continue random walk while another RTC or SC will not be found
    4. New ICs will be recruited according to the following law, where nIC, nRTC, nT - is number of ICs, RTCs and total number of tumor cells in current iteration. $\rho$ is the recruiting coefficient. Also we can set the limit of ICs by **max_immune_cell_count** parameter
    $$R = \rho\frac{nIC(t)\times nRTC(t)}{10^3 + nT(t)}$$

### Therapy impact

Firstly, we must make several assumptions:
- Cancer cells can be divided into two types: drug-resistant cells (SC) and drug-sensitive cells (RTC). 
- Drug is evenly distributed among all cells
- We can affect tumor growth via reducing probability of proliferation, increasing probability of cell death and decreasing $K_c$

Drug can kill RTC, QC, IC with different probabilities:

$$F_i(g) = l_i\times PK\times e^{-c_i(t - n_d\tau)}$$

$$l_i=\frac{l_i\times g}{y'_i\times n_d+1}$$

$$y'_i = \theta\times y_i$$ 

$$ 0< \theta \leq1$$

where i can be (RTC, QC, IC) and $g$ is the drug concentration at each cell. Also therapy affects proliferation potential

$$p_0' = \frac{p_0\times y_{PC}}{n_d^{1/n_{dead}}}$$

Therapy is applied from $t_{ap}$ day with $t_{per}$ intervals and drug concentration remain the same during $\tau$ days after the injection

In summary, relation between the states can be expressed as automaton diagram:
![Alt text](img/diagram.png?raw=true "Optional Title")

## Implementation & architecture 

During development we decided to separate app into two main modules - implementation of cellular automaton itself and visualization. GUI module uses simulation classes as interface getting only grids with color to draw, which eased and fastened development of app.

![Alt text](img/architecture.png?raw=true "Optional Title")
### Model architecture

Model of cellular automaton consists of the following classes:
 - **Grid** - is a class representation of lattice which contains 2d array of cells and takes care of list of **Cell**s. By doing this we save time by iterating over 1-d array to get next states of each cell but not the 2-d array. **Cell** itself contain data about it coordinates, neighboring **Cell**s and **Entity** which it holds
 - **Entity** - is a class to define behavior of each state via overriding next_state method. So, in our implementation classes derived from **Entity** work as states. We have implemented the following **Entity**es: BiologicalCell CancerCell, StemCell, QuiescentCell, NecroticCell, ImmuneCell. Each class has redefined next_state method 
 - **FiniteAutomaton** - main class of model that takes care of calling next_state() methods of each active entity, recruiting new ICs and controlling therapy injections.
 - **Variables** - class that holds all initial parameters as well as other dynamic variables that are needed in runtime

 All, in all this this architecture decisions made development of model very flexible what allowed us to make more experiments on the system

### GUI

### Config file

[Initial parameters](#initial-parameters) have default values in our implementation, but to compare different therapy strategies or various drugs we must vary these parameters, so user must pass a yaml file with settings for each simulation:

```yaml
global:
  yI: 1
simulations:
  simulation-1:
    name: "my-first-simulation"
    yPC: 0.3
```

Each config file must contain global and simulations sections. In global section you can redefine parameters that will be set to all of proposed simulations. In simulations section you can add from 1 to 4 simulations settings. Each simulation section must contain its name and list of parameters that should be changed in this simulation. Names of corresponding parameters are defined in table [Initial parameters](#initial-parameters)

## Simulation demonstrations


## Team
 - [Anton Valihurskyi](https://github.com/BlueSkyAndSomeCurses) - Research, GUI development, computation paralelization
 - [Oleksandra Sherhina](https://github.com/shshrg) - Current state chart creation, simulation video export
 - [Viktoriia Lushpak](https://github.com/linyvez) - Current state chart creation, simulation video export
 - [Maksym Zhuk](https://github.com/Zhukowych) - Research, cellular automaton implementation