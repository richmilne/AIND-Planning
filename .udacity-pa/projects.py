import argparse
import shutil
import os
from udacity_pa import udacity

nanodegree = 'nd889'
projects = ['cargo_planning']
filenames_all = [
  'heuristics_analysis.pdf', 'research_report.pdf',
  'example_spare_tire.py', 'example_birthday_dinner.py', 'example_have_cake.py',
  'my_air_cargo_problems.py', 'my_planning_graph.py',  
  'actions.py', 'planning_problem.py', 'lp_utils.py', 'run_search.py',

  'aimacode/__init__.py', 'aimacode/search.py', 'aimacode/utils.py',
  'tests/__init__.py', 'tests/test_my_planning_graph.py',
                       'tests/test_my_air_cargo_problems.py'
]

def submit(args):
  filenames = []
  for filename in filenames_all:
      if os.path.isfile(filename):
          filenames.append(filename)

  udacity.submit(nanodegree, projects[0], filenames, 
                 environment = args.environment,
                 jwt_path = args.jwt_path)
