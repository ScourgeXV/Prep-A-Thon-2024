# Quantum Computing Problem Statement
## Traffic Congestion Management System

This project involves optimiztion of vehicle paths and signal timings for a given road network graph. 

We are given the graph data of road network, vehicle data and emergency vehicle data. We have created two solver scripts, one for path optimization and other for signal timing optimiztion. Both of them consider the case of emergency vehicles nearby.They can be integrated together to get a single solver which handles all the three problems efficiently.

For running the solvers we would require qiskit python libraries which can be installed by running the following commands

```bash
pip install qiskit-ibm-runtime
```
```bash
pip install qiskit-aer
```

Example inputs are given for our program.

These inputs are then read by the input script. For simplicity we have not integrated input script with solvers.

Then these inputs are given to the two solvers to get our optimization results. In these solvers we have already taken simple inputs so there is no need for a input script.