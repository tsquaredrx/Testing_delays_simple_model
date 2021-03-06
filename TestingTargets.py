import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
from itertools import count

def population_split(total_prevalance, relative_likelihood_in_high_prob_proportion):
    ## ASSUMING THE 'HIGH' GROUP IS 10,000 PEOPLE AND LOW IS 90,000
    if type(total_prevalance) is list:
        high_list, low_list = [], []
        for current_prev in total_prevalance:
            high, low = population_split_calculation(current_prev, relative_likelihood_in_high_prob_proportion)
            high_list.append(high)
            low_list.append(low)
        return high_list, low_list
    else:
        return population_split_calculation(total_prevalance, relative_likelihood_in_high_prob_proportion)

def population_split_calculation(total_prevalance, relative_likelihood_in_high_prob_proportion):
    p = total_prevalance
    q = relative_likelihood_in_high_prob_proportion
    high_number = p*q/(9+q)
    low_number = p - high_number
    return high_number, low_number


def plot_pr_detect_vary_test(prevalance_per_100k=1,
                             target_prob=0.8,
                             tests = 4,
                             max_consecutive_days=28,
                             include_plot_labelling=True,
                             high_prev_pop_rel_likelihood=1,
                             high_prev_testing_proportion=.1,
                             r0=None):
    if high_prev_pop_rel_likelihood == 1:
        if r0 is None:
            prevalance_per_100k = float(prevalance_per_100k)
            days_range = range(1, max_consecutive_days+1)
            pr_detect = [1-binom.cdf(0, tests*1000,
                                     prevalance_per_100k/100000)**days
                         for days in days_range]

        else:
            # prevalance_per_100k = simple_exponential_growth(initial_population=prevalance_per_100k,
            #                           r_eff=r0,
            #                           num_days=max_consecutive_days)
            days_range = range(1, max_consecutive_days+1)

            pr_detect = [1-np.prod([binom.cdf(0, tests*1000, current_prev/100000)
                                    for current_prev in simple_exponential_growth(
                    initial_population=prevalance_per_100k,
                    num_days=days,
                    r_eff=r0)])
                         for days in days_range]
            # days_of_no_transmission_threshold = len(prevalance_per_100k)

    else:
        raise ValueError(f'stratified population has not been implemented')

    plt.plot(days_range, pr_detect, '-', linewidth=4)
    plt.xticks(list(range(0,max_consecutive_days+1,7)))
    if target_prob:
        plt.plot([0, max_consecutive_days], [target_prob]*2, '--')
    if include_plot_labelling:
        plt.xlabel('Consecutive days of no detected transmission')
        # plt.ylabel('Probability of detecting transmission')
    plt.ylim([0, 1])

def plot_pr_detect(prevalance_per_100k=1,
                   days_of_no_transmission_threshold=28,
                   target_prob=0.8,
                   max_tests=16,
                   r0=None,
                   include_plot_labelling=True,
                   high_prev_pop_rel_likelihood=1,
                   high_prev_testing_proportion=.1):

    tests_per_k_per_day_range = range(max_tests + 1)

    if high_prev_pop_rel_likelihood == 1:
        try:
            prevalance_per_100k = float(prevalance_per_100k)
            pr_detect = [1-binom.cdf(0,tests*1000,
                                     prevalance_per_100k/100000)
                         **days_of_no_transmission_threshold
                         for tests in tests_per_k_per_day_range]
        except TypeError:
            if r0 is None:
                raise ValueError("Must input R0")
            prevalance_per_100k = list(prevalance_per_100k)
            pr_detect = [1-np.prod([binom.cdf(0 ,tests*1000,
                                              current_prev/100000)
                                  for current_prev
                                  in prevalance_per_100k])
                         for tests in tests_per_k_per_day_range]
            days_of_no_transmission_threshold = len(prevalance_per_100k)
    else:
        try:
            prevalance_per_100k = float(prevalance_per_100k)
            num_in_10k, num_in_90k = population_split(prevalance_per_100k, high_prev_pop_rel_likelihood)
            pr_detect_10k = [1-binom.cdf(0,high_prev_testing_proportion*tests*1000,
                                     num_in_10k/10000)
                         **days_of_no_transmission_threshold
                         for tests in tests_per_k_per_day_range]

            pr_detect_90k = [1-binom.cdf(0, (1 - high_prev_testing_proportion)*tests*1000,
                                     num_in_90k/90000)
                         **days_of_no_transmission_threshold
                         for tests in tests_per_k_per_day_range]

            pr_detect = [1 - (1 - pr_10k)*(1 - pr_90k) for pr_10k, pr_90k in zip(pr_detect_10k, pr_detect_90k)]

        except TypeError:
            if r0 is None:
                raise ValueError("Must input R0")
            prevalance_per_100k = list(prevalance_per_100k)
            num_in_10k_list, num_in_90k_list = population_split(prevalance_per_100k, high_prev_pop_rel_likelihood)
            pr_detect_10k = [1-np.prod([binom.cdf(0 ,high_prev_testing_proportion*tests*1000,
                                              current_prev/10000)
                                  for current_prev
                                  in num_in_10k_list])
                         for tests in tests_per_k_per_day_range]

            pr_detect_90k = [1-np.prod([binom.cdf(0 ,(1 - high_prev_testing_proportion)*tests*1000,
                                              current_prev/90000)
                                  for current_prev
                                  in num_in_90k_list])
                         for tests in tests_per_k_per_day_range]

            pr_detect = [1 - (1 - pr_10k) * (1 - pr_90k) for pr_10k, pr_90k in zip(pr_detect_10k, pr_detect_90k)]

            days_of_no_transmission_threshold = len(prevalance_per_100k)

    plt.plot(tests_per_k_per_day_range, pr_detect, 'o')
    if target_prob:
        plt.plot([0, max_tests], [target_prob]*2, '--')
    if include_plot_labelling:
        plt.xlabel('Tests per 1000 per day')
        plt.ylabel('Probability of detecting transmission')
    plt.ylim([0, 1])

def plot_pr_detect_increasing(prevalance_per_100k=1,
                              days_of_no_transmission_threshold=28,
                              target_prob=0.8,
                              max_tests=16,
                              r0=1,
                              generation_interval=4.7,
                              include_plot_labelling=True,
                              high_prev_pop_rel_likelihood=1,
                              high_prev_testing_proportion=.1):
    if r0 == 1:
        plot_pr_detect(prevalance_per_100k=prevalance_per_100k,
                       days_of_no_transmission_threshold=days_of_no_transmission_threshold,
                       target_prob=target_prob,
                       max_tests=max_tests,
                       r0=None,
                       include_plot_labelling=include_plot_labelling,
                       high_prev_pop_rel_likelihood=high_prev_pop_rel_likelihood,
                       high_prev_testing_proportion=high_prev_testing_proportion)
    else:
        prev_list = simple_exponential_growth(initial_population=prevalance_per_100k,
                                              r_eff=r0,
                                              num_days=days_of_no_transmission_threshold,
                                              generation_interval=generation_interval)
        plot_pr_detect(prevalance_per_100k=prev_list,
                       days_of_no_transmission_threshold=days_of_no_transmission_threshold,
                       target_prob=target_prob,
                       max_tests=max_tests,
                       r0=r0,
                       include_plot_labelling=include_plot_labelling,
                       high_prev_pop_rel_likelihood=high_prev_pop_rel_likelihood,
                       high_prev_testing_proportion=high_prev_testing_proportion)

def simple_exponential_growth(initial_population=1, r_eff=1.5, num_days=28, generation_interval=4.7):
    daily_multiplier = r_eff ** (1 / generation_interval)
    prev_list = [initial_population * (daily_multiplier ** day) for day in range(num_days)]
    return prev_list


def calc_probabilities(prevalence_per_100k=1,
                       days_of_no_transmission_threshold=28,
                       num_tests=4,
                       r0=1,
                       generation_interval=4.7,
                       high_prev_pop_rel_likelihood=1,
                       high_prev_testing_proportion=.1):

        prevalance_per_100k = simple_exponential_growth(initial_population=prevalence_per_100k,
                                              r_eff=r0,
                                              num_days=days_of_no_transmission_threshold,
                                              generation_interval=generation_interval)

        prevalance_per_100k = list(prevalance_per_100k)
        num_in_10k_list, num_in_90k_list = population_split(prevalance_per_100k, high_prev_pop_rel_likelihood)
        pr_detect_10k = 1 - np.prod([binom.cdf(0, high_prev_testing_proportion * num_tests * 1000,
                                                current_prev / 10000)
                                      for current_prev
                                      in num_in_10k_list])

        pr_detect_90k = 1 - np.prod([binom.cdf(0, (1 - high_prev_testing_proportion) * num_tests * 1000,
                                                current_prev / 90000)
                                      for current_prev
                                      in num_in_90k_list])

        pr_detect = 1 - (1 - pr_detect_10k) * (1 - pr_detect_90k)

        return pr_detect

if __name__ == '__main__':

    create_single_figures = False
    create_multi_panel_figures = False
    create_multi_panel_figures_with_stratified_testing = False
    create_multi_panel_time_to_detection_figures = False

    create_tables_commonwealth = False

    if create_tables_commonwealth:
        # num_test_range = (2, 4, 6, 8, 10)
        num_test_range = (10, 8, 6, 4, 2)
        prev_range = (.5, 1, 2)
        days_range = (14, 28)
        reff_range = (1, 1.1, 1.5)
        for days in days_range:
            for reff in reff_range:
                data = {}
                for prev in prev_range:
                    pr_list = []
                    for test in num_test_range:

                        pr = calc_probabilities(prevalence_per_100k=prev,
                                           days_of_no_transmission_threshold=days,
                                           num_tests=test,
                                           r0=reff)
                        pr_list.append(pr)
                    data[f'Prev = {prev}'] = pr_list
                pd.DataFrame(data).to_csv(f'Prob_detect_figures/cwth_tables_days{days}_reff{reff}.csv')

        print(pr)

    # fig, axs = plt.subplots(2,1)
    # plt.axes(axs[0])
    # plot_pr_detect_vary_test(tests=4, prevalance_per_100k=.5)
    # plt.title('Prevalence = 2/100k')
    # plt.axes(axs[1])
    # plot_pr_detect_vary_test(tests=4, prevalance_per_100k=.5, r0=1.5)
    # plt.title('Prevalence = 2/100k')
    # # plt.savefig('Prob_detect_figures/Consecutive_testing_test_fig.png')
    # plt.show()
    # plt.close()

    prev_list = [0.5, 1, 2]
    days_list = [14, 28]
    target_prob = 0.8
    max_tests = 10
    reff_list = [1, 1.1, 1.5]

    high_prev_likelihood_list = [5, 10]
    high_prev_test_prop_list = [1/3, 1/2, 2/3]

    if create_multi_panel_time_to_detection_figures:
        tests_options = 2, 4
        for tests in tests_options:
            fig, ax = plt.subplots(len(prev_list), len(reff_list))
            plt.subplots_adjust(wspace=0.3, hspace=0.3)
            for prev, prev_index in zip(prev_list, count()):
                for r0, r0_index in zip(reff_list, count()):
                    plt.axes(ax[prev_index, r0_index])
                    plot_pr_detect_vary_test(prevalance_per_100k=prev,
                                             tests=tests,
                                             max_consecutive_days=28,
                                             r0=r0,
                                             include_plot_labelling=False)
                    if r0_index == 0:
                        plt.ylabel(f"Prevalence {prev}")
                    if prev_index == 0:
                        plt.title(f'Reff={r0}')
                    if prev_index == len(prev_list) - 1:
                        plt.xlabel('Days')
            plt.savefig(f'Prob_detect_figures/Probability_of_detection_through_'
                        f'time_with_{tests}_tests.png')
            plt.close()


    if create_multi_panel_figures_with_stratified_testing:
        for r0 in reff_list:
            for high_prev_like in high_prev_likelihood_list:
                for high_prev_test in high_prev_test_prop_list:
                    fig, ax = plt.subplots(len(prev_list), len(days_list))
                    for prev, prev_index in zip(prev_list, count()):
                        for day, day_index in zip(days_list, count()):
                            plt.axes(ax[prev_index, day_index])
                            plot_pr_detect_increasing(prevalance_per_100k=prev,
                                           days_of_no_transmission_threshold=day,
                                           target_prob=0.8,
                                           max_tests=max_tests,
                                           r0=r0,
                                           include_plot_labelling=False,
                                           high_prev_pop_rel_likelihood=high_prev_like,
                                           high_prev_testing_proportion=high_prev_test)
                            plt.xticks(list(range(0,max_tests+1,2)))

                            if prev_index+1 == len(prev_list):
                                plt.xlabel('Tests per 1,000 per day')
                            if (prev_index) == int(len(prev_list)/2) and day_index == 0:
                                plt.ylabel('Probability of detection')
                            if prev_index == 0:
                                plt.title(f'Detection within {day} days')
                            plt.text(6, 0.1, f'{prev} per 100k')

                    plt.savefig(f'Prob_detect_figures/multi_r{r0}_'
                                f'high_prev_like{high_prev_like}_test_prop{high_prev_test}.png')
                    plt.close()



    if create_multi_panel_figures:
        for r0 in reff_list:
            fig, ax = plt.subplots(len(prev_list), len(days_list))
            for prev, prev_index in zip(prev_list, count()):
                for day, day_index in zip(days_list, count()):
                    plt.axes(ax[prev_index, day_index])
                    plot_pr_detect_increasing(prevalance_per_100k=prev,
                                   days_of_no_transmission_threshold=day,
                                   target_prob=0.8,
                                   max_tests=max_tests,
                                   r0=r0,
                                   include_plot_labelling=False)
                    plt.xticks(list(range(0,max_tests+1,2)))

                    if prev_index+1 == len(prev_list):
                        plt.xlabel('Tests per 1,000 per day')
                    if (prev_index) == int(len(prev_list)/2) and day_index == 0:
                        plt.ylabel('Probability of detection')
                    if prev_index == 0:
                        plt.title(f'Detection within {day} days')
                    plt.text(6, 0.1, f'{prev} per 100k')
            plt.savefig(f'Prob_detect_figures/multi_r{r0}.png')
            plt.close()




    if create_single_figures:
        for prev in prev_list:
            for day in days_list:
                for r0 in reff_list:
                    print(f'running prev{prev}, days{day}, r0{r0}')
                    plot_pr_detect_increasing(prevalance_per_100k=prev,
                                   days_of_no_transmission_threshold=day,
                                   target_prob=0.8,
                                   max_tests=16,
                                   r0=r0)

                    if r0 == 1:
                        plt.title(f"Probability of detecting transmission "
                                  f"with\nprevalence {prev}"
                                  f" per 100k within {day} days")
                        plt.savefig(f"Prob_detect_figures/detect_{prev}"
                                    f"_per_100k_in{day}_days.png")
                    else:
                        plt.title(f"Probability of detecting transmission "
                                  f"with\n initial prevalence {prev} and\n"
                                  f"Reff={r0}"
                                  f" per 100k within {day} days")
                        plt.savefig(f"Prob_detect_figures/detect_{prev}"
                                    f"_r0_{r0}"
                                    f"_per_100k_in{day}_days.png")
                    # plt.show()
                    plt.close()