# coding: utf-8

import clinica.pipelines.engine as cpe


class VisualizationMollweid(cpe.Pipeline):
    """VisualizationMollweid - Visualization with Mollweid projection of surface data.

    # TODO : Upgrade to support live projection of native space

    Returns:
        A clinica pipeline object containing the VisualizationMollweid pipeline.
    """

    def check_pipeline_parameters(self):
        """Check pipeline parameters."""
        if 'data_selected' not in self.parameters.keys():
            raise KeyError('Missing compulsory data_selected key in pipeline parameter.')

    def check_custom_dependencies(self):
        """Check dependencies that can not be listed in the `info.json` file."""
        pass

    def get_input_fields(self):
        """Specify the list of possible inputs of this pipeline.

        Returns:
            A list of (string) input fields name.
        """
        return ['input_overlay_lh', 'input_overlay_rh']

    def get_output_fields(self):
        """Specify the list of possible outputs of this pipeline."""
        return ['output_file_png_lh', 'output_file_png_rh']

    def build_input_node(self):
        """Build and connect an input node to the pipeline."""
        from clinica.utils.inputs import clinica_file_reader
        from clinica.utils.exceptions import ClinicaException
        from clinica.utils.input_files import pet_surface_suvr, t1w_freesurfer_mgh, t1w_freesurfer_surface
        import nipype.interfaces.utility as nutil
        import nipype as npe

        read_parameters_node = npe.Node(name="LoadingCLIArguments",
                                        interface=nutil.IdentityInterface(
                                            fields=self.get_input_fields(),
                                            mandatory_inputs=True),
                                        synchronize=True)

        all_errors = []

        # OVERLAY

        if self.parameters['data_selected'] == "suvr":
            try:
                read_parameters_node.inputs.input_overlay_lh = clinica_file_reader(self.subjects,
                                                                      self.sessions,
                                                                      self.bids_directory,
                                                                                   pet_surface_suvr('fdg',
                                                                                                    "fsaverage", 'l',
                                                                                                    True, 'pons',
                                                                                                    self.parameters[
                                                                                                        'fwhm']))
            except ClinicaException as e:
                all_errors.append(e)

            try:
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                          self.sessions,
                                                                          self.caps_directory,
                                                                          pet_surface_suvr('fdg', "fsaverage", 'r', True, 'pons', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)
        else:
            try:
                read_parameters_node.inputs.input_overlay_lh = clinica_file_reader(self.subjects,
                                                                                      self.sessions,
                                                                                      self.caps_directory,
                                                                                      t1w_freesurfer_mgh(self.parameters['data_selected'], "fsaverage", 'l', self.parameters['fwhm']))
                read_parameters_node.inputs.input_overlay_lh = clinica_file_reader(self.subjects,
                                                                                      self.sessions,
                                                                                      self.caps_directory,
                                                                                      t1w_freesurfer_mgh(self.parameters['data_selected'], "fsaverage", 'l', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)

            try:
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                                     self.sessions,
                                                                                     self.caps_directory,
                                                                                     t1w_freesurfer_mgh(self.parameters['data_selected'], "fsaverage", 'l', self.parameters['fwhm']))
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                                     self.sessions,
                                                                                     self.caps_directory,
                                                                                     t1w_freesurfer_mgh(self.parameters['data_selected'], "fsaverage", 'l', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)


        # ERROR

        if len(all_errors) > 0:
            error_message = 'Clinica faced errors while trying to read files in your CAPS directories.\n'
            for msg in all_errors:
                error_message += str(msg)
            raise ClinicaException(error_message)

        # CONNECT TO PIPELINE

        self.connect([
            (read_parameters_node, self.input_node, [('input_overlay_lh', 'input_overlay_lh'),
                                                     ('input_overlay_rh', 'input_overlay_rh')])
        ])

    def build_output_node(self):
        """Build and connect an output node to the pipeline."""
        import nipype.interfaces.utility as nutil
        from nipype.interfaces.io import DataSink
        import nipype.pipeline.engine as npe
        from clinica.utils.nipype import (fix_join, container_from_filename)

        # Write node
        # ----------------------
        write_node = npe.Node(
            name="WriteCaps",
            interface=DataSink()
        )
        write_node.inputs.base_directory = self.caps_directory
        write_node.inputs.parameterization = False

        container_path = npe.Node(
            nutil.Function(
                input_names=['bids_or_caps_filename'],
                output_names=['container'],
                function=container_from_filename),
            name='ContainerPath')

        self.connect([
            (self.input_node, container_path, [('overlay_lh_file', 'bids_or_caps_filename')]),
            (self.input_node, container_path, [('overlay_rh_file', 'bids_or_caps_filename')]),
        ])

        subfolder = 'visualization'
        mod_subfolder = "mollweid"
        self.connect([
            (self.output_node, write_node, [('output_file_png_lh', '@output_file_png_lh'), ('output_file_png_rh', '@output_file_png_rh')])
        ])

        self.connect([
            (container_path, write_node, [(
                (
                    'container', fix_join,
                    'visualization_mollweid', subfolder, mod_subfolder
                ),
                'container')]),
        ])

    def build_core_nodes(self):
        """Build and connect the core nodes of the pipeline."""

        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe
        from .visualization_mollweid_utils import freesurfer2mollweid_full
        # The processing nodes

        freesurfer2mollweid_full = npe.MapNode(
            name='freesurfer2ply_full',
            iterfield=['overlay_lh_file', 'overlay_rh_file'],
            interface=nutil.Function(
                function=freesurfer2mollweid_full,
                input_names=['overlay_lh_file', 'overlay_rh_file'],
                output_names=['output_file_png_lh', 'output_file_png_rh']
            )
        )

        # Connections
        # ----------------------
        self.connect([
            (self.input_node, freesurfer2mollweid_full, [('input_overlay_lh', 'input_overlay_lh'),
                                                     ('input_overlay_rh', 'input_overlay_rh')]),
        ])

        self.connect([
            (freesurfer2mollweid_full, self.output_node, [('output_file_png_lh', 'output_file_png_lh'), ('output_file_png_rh', 'output_file_png_rh')])
        ])

