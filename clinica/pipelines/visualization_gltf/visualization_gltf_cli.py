# coding: utf8

import clinica.engine as ce


class VisualizationGltfCLI(ce.CmdParser):

    def define_name(self):
        """Define the sub-command name to run this pipeline."""
        self._name = 'visualization_gltf'

    def define_description(self):
        """Define a description of this pipeline."""
        self._description = ('T1-Freesurfer and PET-Surface data saved on individual or fsaverage surface in GLTF model compatible with ARBrain and most of Virtual/Augmented reality software')

    def define_options(self):
        """Define the sub-command arguments."""
        from clinica.engine.cmdparser import PIPELINE_CATEGORIES
        # Clinica compulsory arguments (e.g. BIDS, CAPS, group_label)
        clinica_comp = self._args.add_argument_group(PIPELINE_CATEGORIES['CLINICA_COMPULSORY'])
        clinica_comp.add_argument("caps_directory",
                                  help='Path to the CAPS directory.')
        clinica_comp.add_argument("data_selected",
                                  help='Data choosen to be plot (thickness, curv, area, jacobian_white, sulc, volume, suvr.')

        # Optional arguments (e.g. FWHM)
        optional = self._args.add_argument_group(PIPELINE_CATEGORIES['OPTIONAL'])
        optional.add_argument("-base", default="fsaverage",
                              help='Use native or fsaverage.')
        optional.add_argument("-fwhm", default="5",
                              help='If using fsaverage, which fwhm use (0, 5, 10, 15, 20, 25 available).')

        # Clinica standard arguments (e.g. --n_procs)
        self.add_clinica_standard_arguments(add_overwrite_flag=True)

    def run_command(self, args):
        """Run the pipeline with defined args."""
        from networkx import Graph
        from .visualization_gltf_pipeline import VisualizationGltf
        from clinica.utils.ux import print_end_pipeline, print_crash_files_and_exit

        parameters = {
            'data_selected': args.data_selected,
            'base': args.base,
            'fwhm': args.fwhm,
        }

        pipeline = VisualizationGltf(
            caps_directory=self.absolute_path(args.caps_directory),
            tsv_file=self.absolute_path(args.subjects_sessions_tsv),
            base_dir=self.absolute_path(args.working_directory),
            parameters=parameters,
            name=self.name,
            overwrite_caps=args.overwrite_outputs
        )

        if args.n_procs:
            exec_pipeline = pipeline.run(plugin='MultiProc',
                                         plugin_args={'n_procs': args.n_procs})
        else:
            exec_pipeline = pipeline.run()

        if isinstance(exec_pipeline, Graph):
            print_end_pipeline(self.name, pipeline.base_dir, pipeline.base_dir_was_specified)
        else:
            print_crash_files_and_exit(args.logname, pipeline.base_dir)
