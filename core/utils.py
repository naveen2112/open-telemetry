from ajax_datatable import AjaxDatatableView


class CustomDatatable(AjaxDatatableView):
    def get_table_row_id(self, request, obj, i):
        """
        Provides a specific ID for the table row; default: "row-ID"
        Override to customize as required.

        Do to a limitation of datatables.net, we can only supply to table rows
        a id="row-ID" attribute, and not a data-row-id="ID" attribute
        """
        result = ""
        if self.table_row_id_fieldname:
            if type(obj) == dict:
                try:
                    result = self.table_row_id_prefix + str(i + 1)
                except AttributeError:
                    result = ""
            else:
                try:
                    result = self.table_row_id_prefix + str(
                        getattr(obj, self.table_row_id_fieldname)
                    )
                except AttributeError:
                    result = ""
        return result


    def render_column(self, row, column):
        if type(row) == dict:
            value = row[column]
        else:
            value = self.column_obj(column).render_column(row)
        return value


    def prepare_results(self, request, qs):
        json_data = []
        columns = [c["name"] for c in self.column_specs]
        for i, cur_object in enumerate(qs):
            retdict = {
                # fieldname: '<div class="field-%s">%s</div>' % (fieldname, self.render_column(cur_object, fieldname))
                fieldname: self.render_column(cur_object, fieldname)
                for fieldname in columns
                if fieldname
            }

            self.customize_row(retdict, cur_object)
            self.clip_results(retdict)

            row_id = self.get_table_row_id(request, cur_object, i)

            if row_id:
                # "Automatic addition of row ID attributes"
                # https://datatables.net/examples/server_side/ids.html
                retdict["DT_RowId"] = row_id

            json_data.append(retdict)
        return json_data
