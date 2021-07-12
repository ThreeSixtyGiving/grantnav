from django import template
from django.conf import settings
from grantnav.frontend.templatetags.frontend import currency_symbol
import plotly.graph_objs as go
import datetime
from copy import deepcopy
from millify import millify

register = template.Library()

GRAPH_HEIGHT = 160
GRAPH_WIDTH = 320
BAR_COLOUR = '#DE6E26'
PAPER_COLOUR = 'rgba(0,0,0,0)'
GRAPH_DURATION = 20  # Years
YEAR_CUT_OFF = int((datetime.datetime.now() - datetime.timedelta(days=GRAPH_DURATION * 365)).timestamp()) * 1000
TOOLTIP_STYLE = dict(bgcolor="white", font_size=16, font_family="Roboto")


@register.inclusion_tag('components/generic.html', takes_context=True)
def amount_awarded_graph(context):

    try:
        amount_awarded_buckets = context['results']['aggregations']['amountAwardedFixedOriginal']['buckets']

        x = []
        x2 = []
        y = []
        for bucket in amount_awarded_buckets:
            print(bucket)
            x.append('{}{}'.format(currency_symbol(context['currency']), millify(bucket['from'])))
            y.append(bucket['doc_count'])
            x2.append(' - {}{}'.format(currency_symbol(context['currency']), millify(bucket['to']))) if 'to' in bucket else x2.append('+')

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x2, hovertemplate='Amount awarded: %{x}%{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)
        
        fig.update_xaxes(type="category", tickmode="array", tickvals=[1, 3, 5, 7], fixedrange=True, showgrid=False, zeroline=False)
        fig.update_yaxes(fixedrange=True, showgrid=False, showticklabels=False, zeroline=False)

        fig.update_layout(height=GRAPH_HEIGHT, width=GRAPH_WIDTH, plot_bgcolor=PAPER_COLOUR, hoverlabel=TOOLTIP_STYLE)

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

        x = []
        y = []
        early_total = 0
        for bucket in award_year_buckets:
            if bucket['key'] < YEAR_CUT_OFF:
                early_total += bucket['doc_count']
            if bucket['key'] > YEAR_CUT_OFF:
                x.append(bucket['key_as_string'])
                y.append(bucket['doc_count'])

        x, y = (list(sync) for sync in zip(*sorted(zip(x, y))))
        x.insert(0, f'{context["results"]["aggregations"]["earliest_grant"]["hits"]["hits"][0]["_source"]["awardDate"][:4]}+')
        y.insert(0, early_total)

        x2 = deepcopy(x)
        print(YEAR_CUT_OFF)
        x2[0] = f'{context["results"]["aggregations"]["earliest_grant"]["hits"]["hits"][0]["_source"]["awardDate"][:4]} - {datetime.datetime.utcfromtimestamp(YEAR_CUT_OFF/1000).strftime("%Y")}'

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x2, hovertemplate='Date awarded: %{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)
        
        fig.update_xaxes(type="category", tickmode="array", fixedrange=True, showgrid=False, zeroline=False)
        fig.update_yaxes(fixedrange=True, showgrid=False, showticklabels=False, zeroline=False)

        fig.update_layout(height=GRAPH_HEIGHT, width=GRAPH_WIDTH, plot_bgcolor=PAPER_COLOUR, hoverlabel=TOOLTIP_STYLE)

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except Exception as e:
        print(e)
        plot_div = ''

    return {
        'html': plot_div,
    }
