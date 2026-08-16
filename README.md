# Structure
final project
    |-phase 1  
    |    |-requirements.txt
    |    |-cleaning
    |    |    |-cleaning.py
    |    |    |-test_cleaning.py
    |    |    |-clean_delay.csv
    |    |    |-monthly data
    |    |        |-several datafiles 
    |    |-training       
    |         |-train.py
    |         |-test_train.py
    |         |-models
    |-phase 2   
    |    |-app.py
    |    |-clean_delays.csv
    |    |-create_database.py
    |    |-requirements.txt
    |    |-test_app.py
    |-phase 3
    |    |-user_interface.py
    |    |-dashboard.py
    |    |-airport_codes.csv
    |    |-requirements.txt
    |    |-test_frontend.py

            
# Instructions
1. Clone repository

## Phase 1
2. Create virtual environment using p1_requirements.txt
3. Log in to Weights and Biases with 'wandb login' then paste your api key.
4. Navigate to phase 1 folder in cloned repository
5.Create virtual environment using requirements.txt
6. Navigate to cleaning folder and run the clean.py to train and log various models
7. Log in to Weights and Biases using 'wandb login' then paste your api key
8. Navigate to training folder and run train.py
9. Navigate to Weights and Biases Artifacts page in browser
10. For each model link to the registry
11. For the best performing model add a production alias

## Phase 2
12. Navigate to phase 2 folder
13. Create virtual environment using requirements 
14. Set database password using 'set $env:DB_PASSWORD=*password*'
15. Run create_database.py
16. 
17. 