import pandas as pd
from shiny import App, render, ui
import matplotlib.pyplot as plt
import seaborn as sns
import shinyswatch

plt.style.use('ggplot')
path = r'cleaned_data.csv'
df = pd.read_csv(path) # load data
df['year'] = df['REF_DATE'].copy() # copy years to new column for sorting later
df = df.set_index(['Province', 'Municipality', 'REF_DATE']) # re-set the multi-index (lost on import)
provinces = df.index.levels[0].unique().to_list()
comps = [' -none- ','Land Class', 'Municipality Size', 'Growth Class'] # comparison methods for selectiong
meas = ['NDVI', 'Avg Greenness'] # measurements for selection
df2 = df.reset_index() # dataframe for plot #2

# Shiny user interface
app_ui = ui.page_fluid(
    # Titles
    shinyswatch.theme.morph(),
    ui.h1('Greenspace and Vegetation Quality in Canadian Municipalities'),
    ui.h6('John Tweedie, Student #: 400550023'),
    ui.row(
        ui.column(1),
        ui.column(10, 'United Nation\'s Sustainable development Goal #11 aims to increase greenspace (i.e.predominantley vegetated areas) availablility and quality within urban settings. '
                      '(United Nations Department of Economic and Social Affairs, 2023) The "greenness" of a municipality* can refer to the quality and presence of vegetation within a '
                      'municipilty (Statistics Canada, 2023b). Greenness is quantified here by two indicies: "NDVI" and "Average Greenness"'
                      'A Normalized Difference Vegetation Index (NDVI), derived through satellite imagery and remote sensing. '
                      'NDVI values are unitless range from -1 to 1, with larger values representing higher vegetation presence, density, and quality. '
                      'NDVI values are provided as an average across a given municipality. '
                      '"Average Greenness" is the proportion of land within a municipality that has an NDVI over 0.5, indicating the presence of vegetation/greenspace. '),
        ui.column(1),
    ),

    # Upper plot and user inputs
    ui.h6('Plot #1:'),
    ui.h3('Yearly Distributions of Municipality Greenness Levels:'),
    ui.h6('Kernel desnity plots of yearly greenness index values in Canadian municipalities '
          '(population>1,000), grouped by municipality category. (Statistics Canada, 2023a, 2023b)'),
    # selection dropdowns and sliders to update upper chart
    ui.row(
        ui.column(3, ui.input_select(
            'prov', label='Select Province:',
            choices=['Canada (Aggregate)'] + provinces)),
        ui.column(3, ui.input_select(
            'comp', label='Municipality Comparison Method:',
            choices=comps)),
        ui.column(3, ui.input_select(
            'meas', label='Greenness Index:',
            choices=meas)),
        ui.column(3, ui.input_slider(
            'years', label='Display Year Range:',
            value=(2001, 2022), min=2001, max=2022)),
    ),
    ui.output_plot('upper_plot'),

    # Lower plot and user inputs
    ui.h6('Plot #2:'),
    ui.h3('Yearly Greenness Levels of Select Municipalities**'),
    ui.h6('Ordinal plots (based on 2022 values) of yearly greenness index values in Canadian municipalities '
          '(population>5,000), grouped by population growth rate category (Statistics Canada, 2023a, 2023b)'),
    # selection dropdowns and sliders to update lower chart
    ui.row(
        ui.column(3, ui.input_select(
            'prov2', label='Select Province:',
            choices=provinces), selected='Ontario'),
        ui.column(3, ui.input_select(
            'meas2', label='Greenness Index:',
            choices=meas)),
        ui.column(3, ui.input_slider(
            'years2', label='Display Year Range:',
            value=(2001, 2022), min=2001, max=2022)),
    ),
    ui.output_plot('lower_plot'),
    ui.h6('Notes:'),
    ui.row(
        ui.column(12, '* - Municipalities are defined by contiguous areas with a population greater than 1,000 and an '
                      'average population density greater than 400 persons per km\u00b2. '),
        ui.column(12, 'Municipality size classes are defined as follows (Statistics Canada, 2023): '),
        ui.column(12, '     Small: 1,000 to 29,999 population'),
        ui.column(12, '     Medium: between 30,000 to 99,999 population'),
        ui.column(12, '     Large: greater than 100,000 population'),
        ui.column(12, '** - Select municipalities only include those with populations greater than 5000. '
                      'Further, only core urban centres are included (e.g. Toronto), whereas the suburban '
                      'municipalities with contiguous borders to the core are not (e.g. Markham). '),
    ),
    ui.h6('References:'),
    ui.row(
        ui.column(12, 'Statistics Canada. (2023a, January). Population estimates, July 1, by census subdivision, '
                      '2016 boundaries. Retrieved September 25, 2023, '
                      'from https://open.canada.ca/data/en/dataset/6841ba54-09d3-4c12-a2fc-a5064694a860'),
        ui.column(12, 'Statistics Canada. (2023b, June). Urban greenness and normalized difference vegetation index by '
                      '2021 population (Table 38100158). Retrieved September 24, 2023, '
                      'from https://www150.statcan.gc.ca/n1/pub/16-509-x/2016001/1699-eng.htm”'),
        ui.column(12, 'United Nations Department of Economic and Social Affairs. (2023, July). The Sustainable '
                      'Development Goals Report 2023: Special Edition. United Nations. '
                      'https://doi.org/10.18356/97892100249145'),
    ),
)

def server(input, output, session):
    @output
    @render.plot
    def upper_plot():
        # create distribution plots (displots) that update based on user selections
        year_range = [year for year in range(input.years()[0], input.years()[1]+1)] #get range of years from slider
        if input.prov() == 'Canada (Aggregate)': # if Canada is selected, chart the aggregate distibution
            if input.comp() == ' -none- ': # if no comparisons are selected, chart accordingly
                fig_upper = sns.displot(data=df.loc[:,:,year_range], col='year', y=input.meas(),
                                  kind='kde', fill=True, alpha=0.3,
                                  common_norm=False, legend=False)
                fig_upper.fig.suptitle(
                    'Yearly Aggregate Distributions of Canadian Municipality Greenness Levels')
            else: # chart by comparison method
                fig_upper = sns.displot(data=df.loc[:, :, year_range], col='year', y=input.meas(),
                                       kind='kde', hue=input.comp(), fill=True, alpha=0.3,
                                       common_norm=False)
                sns.move_legend(obj=fig_upper, loc='lower right', frameon=True)
                fig_upper.fig.suptitle(
                    'Yearly Aggregate Distributions of Canadian Municipality Greenness Levels by ' + input.comp())
        else:
            if input.comp() == ' -none- ':
                fig_upper = sns.displot(data=df.loc[input.prov(),:,year_range], col='year',
                                  y=input.meas(), kind='kde',
                                  fill=True, alpha=0.3, common_norm=False, legend=False)
                fig_upper.fig.suptitle(
                    'Yearly Aggregate Distributions of Canadian Municipality Greenness Levels')
            else:
                fig_upper = sns.displot(data=df.loc[input.prov(),:,year_range], col='year',
                                  y=input.meas(), kind='kde', hue=input.comp(),
                                  fill=True, alpha=0.3, common_norm=False)
                sns.move_legend(obj=fig_upper, loc='lower right', frameon=True)
                fig_upper.fig.suptitle(
                    'Yearly Aggregate Distributions of Canadian Municipality Greenness Levels by ' + input.comp())
        # figure adjustments
        fig_upper.set_titles(col_template='{col_name}')
        # update axis labels based on selections
        if input.meas() == 'NDVI':
            fig_upper.set_axis_labels(y_var='NDVI (unitless)')
        elif input.meas() == 'Avg Greenness':
            fig_upper.set_axis_labels(y_var='Avg Greenness (% Land Cover)')
            fig_upper.set(ylim=(0, 100))
        fig_upper.set_axis_labels('')
        fig_upper.fig.supxlabel('Density')
        fig_upper.set_xticklabels(rotation=90, fontsize=6)
        fig_upper.set(xticks=fig_upper.axes[0,0].get_xlim()) # remove excessive x-axis (density) labels, keep only largest

        return fig_upper
    @output
    @render.plot
    def lower_plot():
        # create ordinal plots that update based on user selections
        year_range = [year for year in range(input.years2()[0], input.years2()[1] + 1)] # get range of years from slider
        df_plot = df.reset_index() # create a new dataframe without the index (allows us to sort easier for ordinal plots)
        df_plot = df_plot.loc[df_plot['Current Population'] >= 5000]
        if input.meas2() == 'NDVI':
            df_plot = df_plot.sort_values(['Current NDVI','year'], ascending=[True, True]) # sort by current (2022) NDVI value for ordinal plot
            fig_lower = sns.relplot(data=df_plot.loc[(df_plot['Province']==input.prov2())&(df_plot['year'].isin(year_range))],
                                    x='Municipality', y='NDVI', hue='year',
                                    col='Growth Class', kind='scatter', facet_kws={'sharey': True, 'sharex': False},
                                    palette=sns.color_palette('YlOrBr', as_cmap=True), linewidth=0, s=15)

        elif input.meas2() == 'Avg Greenness':
            df_plot = df_plot.sort_values(by=['Current Avg Greenness','year'], ascending=[True, True]) # sort by current (2022) Avg Greenness value for ordinal plot
            fig_lower = sns.relplot(data=df_plot.loc[(df_plot['Province']==input.prov2())&(df_plot['year'].isin(year_range))],
                                    x='Municipality', y='Avg Greenness', hue='year',
                                    col='Growth Class', kind='scatter', facet_kws={'sharey': True, 'sharex': False},
                                    palette=sns.color_palette('YlOrBr', as_cmap=True), linewidth=0, s=15)
        # figure adjustments
        fig_lower.set_xticklabels(rotation=90, fontsize=9)
        for ax in fig_lower.axes.flat:
            ax.set_title(ax.get_title(), fontsize=16)
        fig_lower.set_axis_labels('')
        fig_lower.set_titles(col_template='{col_name}')
        fig_lower.fig.supxlabel('Municipality')
        if input.meas2() == 'NDVI':
            fig_lower.set_axis_labels(y_var='NDVI (unitless)', fontsize=8)
        elif input.meas2() == 'Avg Greenness':
            fig_lower.set_axis_labels(y_var='Avg Greenness (% Land Cover)', fontsize=8)
        sns.move_legend(obj=fig_lower, loc='lower left', frameon=True)

        return fig_lower

app = App(app_ui, server)