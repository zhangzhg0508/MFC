import re

from mfc.printer import cons

import run.engines as engines
import run.input   as input

import common
import build


class MFCRun:
    def __init__(self, mfc):
        self.mfc = mfc

    def validate_job_options(self) -> None:
        if self.mfc.args["cpus_per_node"] != self.mfc.args["gpus_per_node"] \
            and self.mfc.args["gpus_per_node"] != 0:
            raise common.MFCException("RUN: Conflicting job execution parameters. If using GPUs, CPUs per node and GPUs per node must match.")

        if self.mfc.args["nodes"] <= 0:
            raise common.MFCException("RUN: At least one node must be requested.")

        if self.mfc.args["cpus_per_node"] <= 0:
            raise common.MFCException("RUN: At least one CPU per node must be requested.")

        if not common.isspace(self.mfc.args["email"]):
            # https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address
            if not re.match(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?", self.mfc.args["email"]):
                raise common.MFCException(f'RUN: {self.mfc.args["email"]} is not a valid e-mail address.')

        engines.get_engine(self.mfc.args["engine"]).validate_job_options(self.mfc)

    def run(self) -> None:
        cons.print("[bold][u]Run:[/u][/bold]")
        cons.indent()

        if len(self.mfc.args["targets"]) == 0:
            cons.print(f"> No target selected.")
            return

        input_file = input.load(self.mfc.args["input"].strip())

        engine = engines.get_engine(self.mfc.args["engine"])
        engine.init(self.mfc, input_file)

        cons.print(f"Configuration:")
        cons.indent()
        cons.print(f"""\
Input               {self.mfc.args['input']}
Job Name      (-#)  {self.mfc.args['name']}
Engine        (-e)  {self.mfc.args['engine']}
Mode          (-m)  {self.mfc.args['mode']}
Targets       (-t)  {common.format_list_to_string(self.mfc.args['targets'], "None")}
{engine.get_args()}\
""")
        cons.unindent()

        self.validate_job_options()

        for target_name in engine.get_targets(self.mfc.args["targets"]):
            cons.print(f"Running [bold magenta]{target_name}[/bold magenta]:")
            cons.indent()

            input_file.create(target_name)

            build.build_target(self.mfc, target_name)

            engine.run(target_name)
            
            cons.unindent()
    
        cons.unindent()
