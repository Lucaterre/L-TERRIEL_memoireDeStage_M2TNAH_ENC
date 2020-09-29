#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""KRAKEN-BENCHMARK FLASK APP

Author : Lucas Terriel
Date : 22/07/2020

-| Summary |-
=============

Manage web-app side of Kraken-Benchmark


# TODO(Lucas) : --issue : plot deltas (STSig) in same URL:/sequences_to_signals/<int:text_id>
"""

# built-in packages
from datetime import datetime
import io
import os
import uuid
import webbrowser

# external packages
from flask import Flask, render_template, Response, request
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
plt.switch_backend('Agg')
plt.rcParams.update({'figure.max_open_warning': 0})

# local packages
from kb_utils.kb_utils import get_username, arrange_images_in_static
from STS_Tools.SynSemTS import show_diff_color_html, VisualSynTS
from STS_Tools.STSig import SequencesToSignals, PlotSTS


def generate_html_report(metadata: list,
                         model_name: str,
                         list_statistics: list,
                         images: list) -> None:
    """generate a Flask application to display the results
    of the tests in differents HTML templates. Define routes here.

    Note
    ----
    The arguments retrieved come from the kraken_benchmark.py script

    Args:
        metadata (list): differents labels attach to the images if user activate [label]
        model_name (str): name of model
        list_statistics (list): list contains SynSemTS objects
        images (list): list of user's images
    """

    # Alert message and name request :
    os.popen("say -v Victoria Please, your name is required")
    username = get_username()

    # Generate id from uuid and reduce the length of id :
    id_report = str(uuid.uuid1())[:8]

    # Manage static folder with user's images
    arrange_images_in_static(images)

    # Config app and manage directories
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, 'templates')
    statics = os.path.join(root, "static")
    app = Flask("Kraken-Benchmark",
                template_folder=templates_dir,
                static_folder=statics)

    # Jinja filters on templates
    @app.template_filter('datetime_format')
    def datetime_format(value, format_date='%H:%M / %d-%m-%Y'):
        return value.strftime(format_date)

    # Manage routes for Kraken-Benchmark

    @app.route("/")
    def report():
        """renders general dashboard
        """
        return render_template("report.html",
                               date=datetime.now(),
                               labels=metadata,
                               model=model_name,
                               id=id_report,
                               name=username,
                               metrics=list_statistics,
                               size_images=len(images))

    @app.route("/KB-notebook")
    def notebook():
        """ renders research notebook

        note
        ----
        * Update HTML template if the notebook changes in ./Documentation-Research
        * add the notebook images in statics when the notebook is well written
        * - don't forget to change url_for() in HTML template !
        """
        return render_template("research_similarity_notebook.html")


    @app.route("/rat-ob-steps-image-<int:number>.png")
    def plot_rat_ob_steps(number):
        """ renders the ratcliff/obershelp characters steps errors plot
        on main report

        Args:
            number (int): number of reference and prediction texts to display figure associate
        """
        synsemts_object = VisualSynTS(list_statistics[number].source,
                                      list_statistics[number].prediction)
        fig_1 = synsemts_object.plot_hist_ratob_steps(
            title=f'Sequence to sequence steps details for image {number + 1}')
        output_1 = io.BytesIO()
        FigureCanvasAgg(fig_1).print_png(output_1)
        return Response(output_1.getvalue(),
                        mimetype="image/png")

    # graph Levenshtein pairs of characters recurring errors confusion matrix on main report
    @app.route("/ranking_classification_errors/<int:text_id>")
    def ranking_classification_errors(text_id):
        """ renders the ratcliff/obershelp characters steps errors plot

            Args:
                text_id (int): id of reference and prediction texts to display ranking associate
        """
        synsemts_object = VisualSynTS(list_statistics[text_id].source,
                                      list_statistics[text_id].prediction)
        plot_confusion_matrix_pairs_errors(text_id)
        total_pairs_errors = synsemts_object.total_pair_char_errors_max_occurences
        all_ranking = synsemts_object.ranking_pairs_characters_errors_html()
        return render_template("ranking_errors.html",
                               number=text_id,
                               total_pairs_errors=total_pairs_errors,
                               all_ranking=all_ranking)

    @app.route("/confusion-matrix-<int:number>.png")
    def plot_confusion_matrix_pairs_errors(number):
        """ renders the error pair of characters in confusion matrix

        Args:
            number (int): number of reference and prediction texts to display figure associate
        """
        synsemts_object = VisualSynTS(list_statistics[number].source,
                                      list_statistics[number].prediction)
        fig_2 = synsemts_object.plot_pairs_characters_errors_confusion_matrix(
            title=f'Pairs of characters recurring errors for image {number + 1} (10 char max)')
        output_2 = io.BytesIO()
        FigureCanvasAgg(fig_2).print_png(output_2)
        return Response(output_2.getvalue(),
                        mimetype="image/png")

    @app.route("/vs_text/<int:text_id>")
    def show_diff(text_id):
        """ renders versus text function

            Args:
                text_id (int): id of reference and prediction texts to display versus associate
        """
        element = list_statistics[text_id]
        reference = element.source
        prediction = element.prediction
        edit_distance_levensthein = element.edit_distance_levensthein
        return render_template("vs_text.html",
                               reference=reference,
                               prediction=prediction,
                               color_diff_source_prediction=show_diff_color_html(reference,
                                                                                 prediction),
                               edit_distance_levensthein=edit_distance_levensthein)

    @app.route("/sequences_to_signals/<int:text_id>")
    def sequences_to_signals(text_id):
        """renders sequences signals plot

            Args:
                text_id (int): id of reference and prediction texts
                            to display sequences-signals figure associate
        """
        reference = list_statistics[text_id].source
        prediction = list_statistics[text_id].prediction
        object_sts = SequencesToSignals(reference, prediction)
        dictionary_char_posweight_html = object_sts.dictionary_latchar_position_weight_html
        min_interval = int(request.args.get("min_interval", 0))
        max_interval = int(request.args.get("max_interval", 70))
        show_deltas = int(request.args.get("show_deltas", int(False)))
        error_boxes = int(request.args.get("error_boxes", int(True)))
        plot_sequences_signals_png(text_id, min_interval, max_interval, show_deltas, error_boxes)
        return render_template("sequences_to_signals.html",
                               min_interval=min_interval,
                               max_interval=max_interval,
                               show_deltas=show_deltas,
                               error_boxes=error_boxes,
                               number=text_id,
                               reference=reference,
                               prediction=prediction,
                               dictionary_char_posweight_html=dictionary_char_posweight_html)

    @app.route("/sequences-signals-"
               "<int:number>-"
               "<int:min_interval>-"
               "<int:max_interval>-"
               "<int:show_deltas>-"
               "<int:error_boxes>.png")
    def plot_sequences_signals_png(number,
                                   min_interval,
                                   max_interval,
                                   show_deltas,
                                   error_boxes):
        """renders sequences signals plot in sequences_to_signals route with user's parameters

            Args:
                number (int): id of reference and prediction texts to
                            display sequences-signals figure associate
                min_interval (int): begin position of char in reference and prediction sequence
                max_interval (int): end position of char in reference and prediction sequence
                show_deltas (bool): display deltas (option)
                error_boxes (bool): display error boxes (option)
        """
        object_sts = SequencesToSignals(list_statistics[number].source,
                                        list_statistics[number].prediction)
        object_plotsts = PlotSTS(object_sts.sequence_reference,
                                 object_sts.sequence_prediction,
                                 object_sts.sequence_reference_encrypt,
                                 object_sts.sequence_prediction_encrypt,
                                 object_sts.sequence_reference_steps,
                                 object_sts.sequence_prediction_steps,
                                 object_sts.dictionary_latchar_position_weight,
                                 object_sts.list_deltas)
        show_deltas = bool(show_deltas)
        error_boxes = bool(error_boxes)
        fig_sequences_signals = \
            object_plotsts._plot_sentences_signal(sample_b=min_interval,
                                                  sample_e=max_interval,
                                                  average_deltas_scatter=show_deltas,
                                                  error_boxes=error_boxes,
                                                  title=f"Sequences to signals for "
                                                        f"image {number + 1} "
                                                        f"with parameters : "
                                                        f"interval={min_interval, max_interval} "
                                                        f"| deltas={show_deltas} | "
                                                        f"errors boxes={error_boxes}")

        output = io.BytesIO()
        FigureCanvasAgg(fig_sequences_signals).print_png(output)
        return Response(output.getvalue(), mimetype="image/png")

    """-- issue : Route for plotting deltas

    @app.route("/deltas-prob-<int:number>.png")
    def plot_deltas_prob_png(number):
        object_STS = SequencesToSignals(list_statistics[number].source, list_statistics[number].prediction)
        object_plotSTS = PlotSTS(object_STS.sequence_reference,
                                 object_STS.sequence_prediction,
                                 object_STS.sequence_reference_encrypt,
                                 object_STS.sequence_prediction_encrypt,
                                 object_STS.sequence_reference_steps,
                                 object_STS.sequence_prediction_steps,
                                 object_STS.dictionary_latchar_position_weight,
                                 object_STS.list_deltas)

        fig_deltas_probas = object_plotSTS._plot_probabilities()

        output = io.BytesIO()
        FigureCanvasAgg(fig_deltas_probas).print_png(output)
        return Response(output.getvalue(), mimetype="image/png")"""

    # error routes
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html')

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html')

    # open the localhost on web browser
    webbrowser.open('http://127.0.0.1:5000/')

    # run app on localhost
    app.run()
