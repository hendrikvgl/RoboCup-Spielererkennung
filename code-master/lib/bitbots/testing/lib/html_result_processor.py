from datetime import datetime


class BitBotsHtmlResultBuffer():
    """ This class is responsible for creating a section on the HTML page which
        gives an overview over the test suites """

    CSS = """
        <style>
            .rand {
                border: 2px solid black;
                width: 100%;
                height: 250px;
                background-color: white;
            }

            #row {
                width: 100%;
            }

            #short_name {
                width: 20%;
                font-weight: bold;
            }

            #statistics {
                width: 20%;
            }
            #description {
                width: 50%;
            }
            #more_info {
                width: 10%;
                cursor: pointer;
                //height: 50px;
            }
            #more_info:hover {
                background-color: #aaf;
            }
            td.normal {
                background-color: lightgray;
                padding: 5px;
            }
            td.error { background-color: #f66; font-size: 14px;}
            td.failure { background-color: #d99; font-size: 14px;}
            td.skip { background-color: #ff5; font-size: 14px;}
            td.unexpected_success { background-color: #f60; font-size: 14px;}
            td.success { background-color: #6f6; font-size: 14px;}
            td.expected_failure { background-color: #6f6; font-size: 14px;}
        </style>
        <script>
           function toggle(control){
                var elem = document.getElementById(control);
                console.log(document);
                console.log(elem);

                if(elem.style.display == "none"){
                    elem.style.display = "block";
                }else{
                    elem.style.display = "none";
                }
            }
        </script>
    """

    START = """
        <html>
        <div style"padding: 5px; width=100%%;">
            <div style="font-size: 16px; font-weight: bold;">RoboCup Bit-Bots Unit-Tests / %(date)s / TODO Git Revision</div>
        </div>
        <hr>
            Run single tests by providing <i>class.testcase</i> as an argument to the <i>run-python-tests</i> script!
        <hr>
        <table>
    """

    END = """
        </table>
        </html>
    """

    HTML = """
        <table style="width: 100%%">
        <tr id="row">
            <td class="normal" id="short_name">%(suite_short_name)s</td>
            <td class="normal" id="description">%(description)s</td>
            <td class="normal" style="text-align: center;" id="statistics">
                <div>
                    <div style="float: left; width: %(failure_bar)s%%; background-color: red; display: %(failure_display)s">
                        <div style="margin: 2px">%(failure)s</div>
                    </div>
                    <div style="float: left; width: %(success_bar)s%%; background-color: green; display: %(success_display)s">
                        <div style="margin: 2px">%(success)s</div>
                    </div>
                    <div style="float: left; width: %(skip_bar)s%%; background-color: #ff5; display: %(skip_display)s">
                        <div style="margin: 2px">%(skips)s</div>
                    </div>
                    <div style="clear:both"></div>
                </div>
            </td>
            <td class="normal" id="more_info">
                <div style="margin: 2px; background-color: #67f; font-size: 20px; text-align: center" onclick="toggle('%(suite_short_name)s')">Details</div>
            </td>
        </tr>
        </table>
        <div id="%(suite_short_name)s" style="display: none; padding: 10px;">
            <table style="width: 100%%">
                %(detailed_info)s
            </table>
        </div>
    """

    DETAILED_SNIPPET = """
        <tr id="row">
            <td style="width: 20%%; font-weight: bold;" class="%(result_class)s">%(result_class)s</td>
            <td style="width: 40%%;" class="%(result_class)s">%(test_name)s</td>
            <td style="width: 40%%;" class="%(result_class)s">%(exception)s</td>
        </tr>
    """

    def __init__(self):
        self._buffer = BitBotsHtmlResultBuffer.CSS + BitBotsHtmlResultBuffer.START % {
            "date": datetime.today()
        }

    @property
    def buffer(self):
        return self._buffer + BitBotsHtmlResultBuffer.END

    def add_test_results(self, suite, result):
        # Calculate the visible stats for the html element
        success, failure, skips = result.get_general_stats()

        # The number of total tests run
        total = float(success + failure + skips)

        # Calculating how high the bars need to be in pixel
        success_bar, failure_bar = 0, 0
        if success != 0:
            success_bar = 100 * (success / total)

        if failure != 0:
            failure_bar = 100 * (failure / total)

        skip_bar = 100 - success_bar - failure_bar

        if skip_bar < 1E-6:
            skip_bar = 0


        # Prepare the more detailed result snippet which can be inspected on demand
        detailed_info = ""

        # Add all errors, skips and failures first
        for testname, test_result in result.test_results.items():
            if test_result.get('marker') not in ["success", "expected_failure"]:
                detailed_info += BitBotsHtmlResultBuffer.DETAILED_SNIPPET % {
                    "test_name": testname,
                    "result_class": test_result.get('marker', "unknown"),
                    "exception": test_result.get('error', ""),
                    "suite_short_name": suite.short_name
                }

        # Add all successes and expected failures then
        for testname, test_result in result.test_results.items():
            if test_result.get('marker') in ["success", "expected_failure"]:
                detailed_info += BitBotsHtmlResultBuffer.DETAILED_SNIPPET % {
                    "test_name": testname,
                    "result_class": test_result.get('marker', "unknown"),
                    "exception": test_result.get('error', ""),
                    "suite_short_name": suite.short_name
                }


        # Really put all the things together
        html_result = BitBotsHtmlResultBuffer.HTML % {
            "suite_short_name": suite.short_name,
            "description": suite.description,
            "success": success,
            "failure": failure,
            "skips": skips,
            "success_bar": success_bar,
            "failure_bar": failure_bar,
            "skip_bar": skip_bar,
            "success_display": 'none' if success_bar == 0 else 'block',
            "failure_display": 'none' if failure_bar == 0 else 'block',
            "skip_display": 'none' if skip_bar == 0 else 'block',
            "detailed_info": detailed_info
        }
        self._buffer += html_result




