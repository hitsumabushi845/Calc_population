import json
import sys
import numpy as np
from Calc_Populations_funcs_ECCSjson import readorbitsfile_forCalcAssignmentRatio

def setSingletTripletRatio():
    try:
        singletRatio = float(input('For SINGLET > '))
        tripletRatio = float(input('For TRIPLET > '))
    except ValueError:
        print('Wrong(or Unexpected) character(s).\nPlease type positive real number or natural number.')
        return 1.0, 3.0

    return singletRatio, tripletRatio

def calculateCrossSectionAssignmentRatio(singletRatio=1, tripletRatio=3, Js=None, J=None):
    if Js == None and J == None:
        # for singlet finestructure level
        singlet_fraction = singletRatio/(singletRatio + tripletRatio)
        return singlet_fraction
    else:
        # for triplet finestructure level
        triplet_fraction = tripletRatio/(singletRatio + tripletRatio)
        stastical_weight_ratio = (2*J + 1)/float(2*sum(Js)+len(Js))
        return triplet_fraction * stastical_weight_ratio

def makeArbitraryProductionRatioDatafile(inProgram=False):

    nlJ_parameters_dict, nl_to_nlJ_map_dict, ordered_nl_list, ordered_nlJ_list = readorbitsfile_forCalcAssignmentRatio('He')

    print('Choose the procedure of making Production Ratio datafile:')
    print('1. Apply equal singlet-triplet production ratio to all nl states.')
    print('2. Apply different singlet-triplet production ratio to each nl state.')

    try:
        datafileMenuNumber = int(input('Please type the number...(1 or 2) > '))
        print(datafileMenuNumber)
    except ValueError:
        print('Wrong(or Unexpected) character(s).\nThe procedure 1 was chosen.')
        datafileMenuNumber = 1

    AssignmentRatio_dict = {}
    if datafileMenuNumber == 1:
        print('here is 1')

        print('Please type singlet-triplet RATIO.')
        singletRatio, tripletRatio = setSingletTripletRatio()

        newAssignmentRatio = {}
        for nl in ordered_nl_list:
            print('For {} state'.format(nl))
            if nl == '1s1s':
                newAssignmentRatio[nl_to_nlJ_map_dict[nl][0]] = 1.0
                continue
            triplets = []
            Js = []
            for nlJ in nl_to_nlJ_map_dict[nl]:
                print(nlJ.split('_')[1])
                if nlJ.split('_')[1] == 'triplet':
                    triplets.append([nlJ, nlJ_parameters_dict[nlJ]['total_angular_momentum']])
                    Js.append(nlJ_parameters_dict[nlJ]['total_angular_momentum'])
                else:
                    newAssignmentRatio[nlJ] = calculateCrossSectionAssignmentRatio(singletRatio, tripletRatio)
            for triplet in triplets:
                newAssignmentRatio[triplet[0]] = calculateCrossSectionAssignmentRatio(singletRatio, tripletRatio, Js, triplet[1])

        if '--debug' in sys.argv:
            for nlJ, AR in sorted(newAssignmentRatio.items(), key=lambda x:x[0]):
                print('{} = {}'.format(nlJ, AR))

        if inProgram == True:
            return newAssignmentRatio
        else:
            print('Please type the output filename.')
            outputfilename = input('> ')
            outputfile = open(outputfilename, 'w')
            json.dump(newAssignmentRatio, outputfile, indent=2, sort_keys=True)
            return 0

    elif datafileMenuNumber == 2:
        print('here is 2')
        newAssignmentRatio = {}
        for nl in ordered_nl_list:
            print('For {} state'.format(nl))
            if nl == '1s1s':
                newAssignmentRatio[nl_to_nlJ_map_dict[nl][0]] = 1.0
                continue
            print('Please type singlet-triplet RATIO for {} configuration.'.format(nl))
            singletRatio, tripletRatio = setSingletTripletRatio()
            triplets = []
            Js = []
            for nlJ in nl_to_nlJ_map_dict[nl]:
                print(nlJ.split('_')[1])
                if nlJ.split('_')[1] == 'triplet':
                    triplets.append([nlJ, nlJ_parameters_dict[nlJ]['total_angular_momentum']])
                    Js.append(nlJ_parameters_dict[nlJ]['total_angular_momentum'])
                else:
                    newAssignmentRatio[nlJ] = calculateCrossSectionAssignmentRatio(singletRatio, tripletRatio)
            for triplet in triplets:
                newAssignmentRatio[triplet[0]] = calculateCrossSectionAssignmentRatio(singletRatio, tripletRatio, Js, triplet[1])

        if '--debug' in sys.argv:
            for nlJ, AR in sorted(newAssignmentRatio.items(), key=lambda x:x[0]):
                print('{} = {}'.format(nlJ, AR))

        if inProgram == True:
            return newAssignmentRatio
        else:
            print('Please type the output filename.')
            outputfilename = input('> ')
            outputfile = open(outputfilename, 'w')
            json.dump(newAssignmentRatio, outputfile, indent=2, sort_keys=True)
            return 0
            

    else:
        print('Wrong(or Unexpected) number.\nPlease type 1 or 2.')

if __name__ == '__main__':
    makeArbitraryProductionRatioDatafile()
