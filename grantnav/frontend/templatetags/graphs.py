from django import template
from django.conf import settings
from grantnav.frontend.templatetags.frontend import currency_symbol
import plotly.graph_objs as go
import datetime
from copy import deepcopy
from millify import millify

register = template.Library()

AMOUNT_AWARDED_GRAPH_HEIGHT = 160
AWARD_DATE_GRAPH_HEIGHT = 180
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
        x_labels = []
        y = []
        for bucket in amount_awarded_buckets:
            x.append('{}{}'.format(currency_symbol(context['currency']), millify(bucket['from'])))
            y.append(bucket['doc_count'])
            x_labels.append(' - {}{}'.format(currency_symbol(context['currency']), millify(bucket['to']))) if 'to' in bucket else x_labels.append('+')

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x_labels, hovertemplate='Amount awarded: %{x}%{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)

        fig.update_xaxes(type="category", tickmode="array", tickvals=[1, 3, 5, 7], fixedrange=True, showgrid=False, zeroline=False)
        fig.update_yaxes(fixedrange=True, showgrid=False, showticklabels=False, zeroline=False)

        fig.update_layout(height=AMOUNT_AWARDED_GRAPH_HEIGHT, width=GRAPH_WIDTH, plot_bgcolor=PAPER_COLOUR, hoverlabel=TOOLTIP_STYLE)

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
        x.insert(0, 'Older')
        y.insert(0, early_total)

        x_labels = deepcopy(x)
        x_labels[0] = f'{context["results"]["aggregations"]["earliest_grant"]["hits"]["hits"][0]["_source"]["awardDate"][:4]} - {datetime.datetime.utcfromtimestamp(YEAR_CUT_OFF/1000).strftime("%Y")}'

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x_labels, hovertemplate='Date awarded: %{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)

        fig.update_xaxes(type="category", tickmode="array", fixedrange=True, showgrid=False, zeroline=False, tickangle=45)
        fig.update_yaxes(fixedrange=True, showgrid=False, showticklabels=False, zeroline=False)

        fig.update_layout(height=AWARD_DATE_GRAPH_HEIGHT, width=GRAPH_WIDTH, plot_bgcolor=PAPER_COLOUR, hoverlabel=TOOLTIP_STYLE)

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except Exception as e:
        print(e)
        plot_div = ''

    return {
        'html': plot_div,
    }


@register.inclusion_tag('components/generic.html', takes_context=True)
def amount_awarded_widget(context):

    try:
        amount_awarded_buckets = context['results']['aggregations']['amountAwardedFixedOriginal']['buckets']

        x = []
        x_labels = []
        y = []
        for bucket in amount_awarded_buckets:
            x.append('{}{}'.format(currency_symbol(context['currency']), millify(bucket['from'])))
            y.append(bucket['doc_count'])
            x_labels.append(' - {}{}'.format(currency_symbol(context['currency']), millify(bucket['to']))) if 'to' in bucket else x_labels.append('+')

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x_labels, hovertemplate='Amount awarded: %{x}%{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)

        fig.update_xaxes(title="Amount awarded ({})".format(currency_symbol(context['currency'])), type="category", tickmode="array", fixedrange=True, showgrid=True, zeroline=False)
        fig.update_yaxes(title="# of Grants", fixedrange=True, showgrid=True, showticklabels=True, zeroline=False)

        fig.update_layout(
            plot_bgcolor=PAPER_COLOUR,
            hoverlabel=TOOLTIP_STYLE,
            font=dict(
                family="Arial",
                size=16,
                color='#000000'
            )
        )

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except Exception as e:
        print('error: ', e)
        plot_div = ''

    return {
        'html': plot_div,
    }


@register.inclusion_tag('components/generic.html', takes_context=True)
def award_date_widget(context):

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
        x.insert(0, 'Older')
        y.insert(0, early_total)

        x_labels = deepcopy(x)
        x_labels[0] = f'{context["results"]["aggregations"]["earliest_grant"]["hits"]["hits"][0]["_source"]["awardDate"][:4]} - {datetime.datetime.utcfromtimestamp(YEAR_CUT_OFF/1000).strftime("%Y")}'

        layout = go.Layout(
            margin=go.layout.Margin(l=50, r=0, b=20, t=0),
            paper_bgcolor=PAPER_COLOUR,
        )

        fig = go.Figure(data=go.Bar(x=x, y=y, text=x_labels, hovertemplate='Date awarded: %{text}' + '<br>Total grants: %{y}<br><extra></extra>',), layout=layout)

        fig.update_xaxes(title="Year awarded", type="category", tickmode="array", fixedrange=True, showgrid=True, zeroline=False, tickangle=45)
        fig.update_yaxes(title="# of Grants", fixedrange=True, showgrid=True, showticklabels=True, zeroline=False)

        fig.update_layout(
            plot_bgcolor=PAPER_COLOUR,
            hoverlabel=TOOLTIP_STYLE,
            font=dict(
                family="Arial",
                size=16,
                color='#000000'
            )
        )

        fig.update_traces(marker_color=BAR_COLOUR)

        plot_div = fig.to_html(full_html=False, include_plotlyjs=settings.PLOTLY_JS_CDN, config={'displayModeBar': False})

    except Exception as e:
        print(e)
        plot_div = ''

    return {
        'html': plot_div,
    }
