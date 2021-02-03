# coding: utf-8

import clinica.pipelines.engine as cpe


class VisualizationGltf(cpe.Pipeline):
    """VisualizationGltf - Visualization by converting in GLTF file.

    Returns:
        A clinica pipeline object containing the VisualizationGltf pipeline.
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
        return ['input_overlay_lh',
                'input_overlay_rh',
                'input_surface_lh', 'input_surface_rh']

    def get_output_fields(self):
        """Specify the list of possible outputs of this pipeline."""
        return ['output_file_gltf_lh', 'output_file_gltf_rh']

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
                                                                                                    self.parameters[
                                                                                                        'base'], 'l',
                                                                                                    True, 'pons',
                                                                                                    self.parameters[
                                                                                                        'fwhm']))
            except ClinicaException as e:
                all_errors.append(e)

            try:
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                          self.sessions,
                                                                          self.caps_directory,
                                                                          pet_surface_suvr('fdg', self.parameters['base'], 'r', True, 'pons', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)
        else:
            try:
                read_parameters_node.inputs.input_overlay_lh = clinica_file_reader(self.subjects,
                                                                                      self.sessions,
                                                                                      self.caps_directory,
                                                                                      t1w_freesurfer_mgh(self.parameters['data_selected'], self.parameters['base'], 'l', self.parameters['fwhm']))
                read_parameters_node.inputs.input_overlay_lh = clinica_file_reader(self.subjects,
                                                                                      self.sessions,
                                                                                      self.caps_directory,
                                                                                      t1w_freesurfer_mgh(self.parameters['data_selected'], self.parameters['base'], 'l', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)

            try:
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                                     self.sessions,
                                                                                     self.caps_directory,
                                                                                     t1w_freesurfer_mgh(self.parameters['data_selected'], self.parameters['base'], 'l', self.parameters['fwhm']))
                read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                                     self.sessions,
                                                                                     self.caps_directory,
                                                                                     t1w_freesurfer_mgh(self.parameters['data_selected'], self.parameters['base'], 'l', self.parameters['fwhm']))
            except ClinicaException as e:
                all_errors.append(e)

        # SURFACE

        try:
            read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                               self.sessions,
                                                                               self.caps_directory,
                                                                               t1w_freesurfer_surface(self.parameters['base'], 'l'))
        except ClinicaException as e:
            all_errors.append(e)

        try:
            read_parameters_node.inputs.input_overlay_rh = clinica_file_reader(self.subjects,
                                                                               self.sessions,
                                                                               self.caps_directory,
                                                                               t1w_freesurfer_surface(self.parameters['base'], 'r'))
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
                                                     ('input_overlay_rh', 'input_overlay_rh'),
                                                     ('input_surface_lh', 'input_surface_lh'),
                                                     ('input_surface_rh', 'input_surface_rh')])
        ])

    def build_output_node(self):
        """Build and connect an output node to the pipeline."""
        import nipype.interfaces.utility as nutil
        from nipype.interfaces.io import DataSink
        import nipype.pipeline.engine as npe
        from clinica.utils.nipype import (fix_join, container_from_filename)
        from clinica.utils.filemanip import get_subject_id

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
            (self.input_node, container_path, [('surface_lh_file', 'bids_or_caps_filename')]),
            (self.input_node, container_path, [('surface_rh_file', 'bids_or_caps_filename')]),
        ])

        subfolder = 'visualization'
        mod_subfolder = "gltf"
        self.connect([
            (self.output_node, write_node, [('output_file_gltf_lh', '@output_file_gltf_lh'), ('output_file_gltf_rh', '@output_file_gltf_rh')])
        ])

        self.connect([
            (container_path, write_node, [(
                (
                    'container', fix_join,
                    'visualization_gltf', subfolder, mod_subfolder
                ),
                'container')]),
        ])

    def build_core_nodes(self):
        """Build and connect the core nodes of the pipeline."""

        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe
        from .visualization_gltf_utils import freesurfer2ply_full, ply2gltf_full
        # The processing nodes

        freesurfer2ply_full = npe.MapNode(
            name='freesurfer2ply_full',
            iterfield=['overlay_lh_file', 'overlay_rh_file', 'surface_lh_file', 'surface_rh_file'],
            interface=nutil.Function(
                function=freesurfer2ply_full,
                input_names=['overlay_lh_file', 'overlay_rh_file', 'surface_lh_file', 'surface_rh_file'],
                output_names=['output_file_ply_lh', 'output_file_ply_rh']
            )
        )


        ply2gltf_full = npe.MapNode(
            name='ply2gltf',
            iterfield=['output_file_ply_lh', 'output_file_ply_rh'],
            interface=nutil.Function(
                function=ply2gltf_full,
                input_names=['output_file_ply_lh', 'output_file_ply_rh'],
                output_names=['output_file_gltf_lh', 'output_file_gltf_rh']
            )
        )

        # Connections
        # ----------------------
        self.connect([
            (self.input_node, freesurfer2ply_full, [('input_overlay_lh', 'input_overlay_lh'),
                                                     ('input_overlay_rh', 'input_overlay_rh'),
                                                     ('input_surface_lh', 'input_surface_lh'),
                                                     ('input_surface_rh', 'input_surface_rh')]),
        ])

        self.connect([
            (freesurfer2ply_full, ply2gltf_full, [('output_file_ply_lh', 'output_file_ply_lh'), ('output_file_ply_rh', 'output_file_ply_rh')]),
            (ply2gltf_full, self.output_node, [('output_file_gltf_lh', 'output_file_gltf_lh'), ('output_file_gltf_rh', 'output_file_gltf_rh')])
        ])

