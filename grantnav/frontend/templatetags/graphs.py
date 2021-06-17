from django import template
from django.conf import settings
from grantnav.frontend.templatetags.frontend import currency_symbol
from plotly.offline import plot
import plotly.graph_objs as go

register = template.Library()

GRAPH_HEIGHT = 160
GRAPH_WIDTH = 320
BAR_COLOUR = '#DE6E26'
PAPER_COLOUR = 'rgba(0,0,0,0)'
YEAR_CUT_OFF = 1009843200000 #2002

@register.inclusion_tag('components/generic.html', takes_context=True)
def amount_awarded_graph(context):

    try:
        amount_awarded_buckets = context['results']['aggregations']['amountAwardedFixedOriginal']['buckets']

        x=[]
        y=[]
        for bucket in amount_awarded_buckets:
            x.append('{}{:,.0f}'.format(currency_symbol(context['currency']), bucket['from']))
            y.append(bucket['doc_count'])


        layout = go.Layout(
            margin=go.layout.Margin(l=50,r=0,b=20,t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y), layout=layout)
        
        fig.update_xaxes(title="Value (log)", type="category", tickmode="array", tickvals=[1,4,7])
        fig.update_yaxes(title="Grants")

        fig.update_layout(height=GRAPH_HEIGHT,width=GRAPH_WIDTH)

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except Exception as e:
        print('error: ', e)
        plot_div = ''

    return {
        'html': plot_div,
    }


@register.inclusion_tag('components/generic.html', takes_context=True)
def award_date_graph(context):

    try:
        award_year_buckets = context['results']['aggregations']['awardYearOriginal']['buckets']

        x=[]
        y=[]
        for bucket in award_year_buckets:
            if bucket['key'] > YEAR_CUT_OFF:
                x.append(bucket['key_as_string'])
                y.append(bucket['doc_count'])

        x,y = (list(sync) for sync in zip(*sorted(zip(x, y))))

        layout = go.Layout(
            margin=go.layout.Margin(l=50,r=0,b=20,t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y), layout=layout)
        
        fig.update_xaxes(title="Year", type="category", tickmode="array", tickvals=[1,4,7,10,13,16])
        fig.update_yaxes(title="Grants")

        fig.update_layout(height=GRAPH_HEIGHT,width=GRAPH_WIDTH)

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except:
        plot_div = ''

    return {
        'html': plot_div,
    }
