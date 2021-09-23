from pyperplan.planner import _parse, _ground
from pyperplan.heuristics.landmarks import get_landmarks
import os
import tarfile
import pandas as pd

class ExtractLandmarks():
    def __init__(self, *args):
        self.counter = 1
        self.landmarks = {}
        if len(args) == 1:
            self.__unpackTar(*args)
        elif len(args) == 3:
            self.__unpackFiles(*args)
        else:
            raise TypeError("Incorrect number of arguments.")

    def __unpackFiles(self, domaindir, goalsdir, templatedir):
        # Domain file
        self.domainfile = os.path.abspath(domaindir)
        # Get the goals from the goal file
        with open(goalsdir) as goalsfile:
            self.goals = goalsfile.read().splitlines()
        # Get the task template from the template file
        with open(templatedir) as templatefile:
            self.template = templatefile.read()
        self.__populate()

    def __unpackTar(self, tardir):
        # Unpacking TAR files
        with tarfile.open(tardir, 'r:bz2') as tar:
            tar.extract('domain.pddl', path="temp")
            self.domainfile = os.path.abspath('temp/domain.pddl')
            self.goals = tar.extractfile('hyps.dat').read().decode('utf-8').splitlines()
            self.template = tar.extractfile('template.pddl').read().decode('utf-8')
        self.__populate()

    def __populate(self):
        # Iterate through each goal and generate a new task file for each
        for goal in self.goals:
            fname = f"task{self.counter}"
            task = self.template.replace("<HYPOTHESIS>", goal)
            with open(f"temp/{fname}.pddl", "w") as create:
                create.write(task)
            landmarks = self.__extract(f"temp/{fname}.pddl")
            self.landmarks[fname] = landmarks
            self.counter += 1

    def __extract(self, fname):
        # Extract landmarks given the filename
        parsed = _parse(self.domainfile, fname)
        task = _ground(parsed)
        landmarks = get_landmarks(task)
        return landmarks 

    def __getitem__(self, fname):
        # Returns the landmarks of the given task.
        try:
            return self.landmarks[fname]
        except:
            return None

    def intersection(self):
        # Returns the landmark intersection of all goals.
        return set.intersection(*list(self.landmarks.values()))

    def table(self):
        # Return a table of the landmark intersection for each pair of goals.
        data = [[set.intersection(valueb, valuea) for keyb, valueb in self.landmarks.items()] for keya, valuea in self.landmarks.items()]
        return pd.DataFrame(data)

if __name__ == "__main__":
    # Defining constants
    EXPERIMENTS_DIR = 'experiments/raw'
    EXPERIMENTS_TAR_DIR = 'experiments/tar'
    RESULTS_DIR = 'results'

    # Iterate through each problem set
    for _, dirs, _ in os.walk(EXPERIMENTS_DIR):
        for dname in dirs:
            print(f"Extracting landmarks for {dname}")
            domaindir = f"{EXPERIMENTS_DIR}/{dname}/domain.pddl"
            hypsdir = f"{EXPERIMENTS_DIR}/{dname}/hyps.dat"
            templatedir = f"{EXPERIMENTS_DIR}/{dname}/template.pddl"
            extraction = ExtractLandmarks(domaindir, hypsdir, templatedir)
            print(extraction.table())

    # For TAR files
    '''
    for _, _, files in os.walk(EXPERIMENTS_TAR_DIR):
        for tarfname in files:
            extraction = ExtractLandmarks(f"{EXPERIMENTS_TAR_DIR}/{tarfname}")
    '''


