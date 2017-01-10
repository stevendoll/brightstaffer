
    $(document).ready(function(){

            $('#loading-example-btn').click(function () {
                btn = $(this);
                simpleLoad(btn, true)
                simpleLoad(btn, false)
            });

            $('.dataTables').DataTable({
                pageLength: 10,
                responsive: true,
                dom: '<"col-sm-4 col-md-4 p-a-0 m-t m-b-lg"B><"col-sm-4 col-md-4 p-a-0 m-t small text-muted text-center"i><"col-sm-4 col-md-4 p-a-0 m-t input-group-sm small"f>rt<"col-sm-6 col-md-6 p-a-0 m-t-md small input-group-sm"l><"col-sm-6 col-md-6 p-a-0 m-t-md small input-group-sm"p><"clear">',

select: {
            style: 'multi'
        },
                buttons: [
                    {extend: 'copy', className: 'btn btn-default btn-sm', title: 'Copy'},
                    {extend: 'csv', className: 'btn btn-default btn-sm', title: 'CSV'},
                    {extend: 'excel', className: 'btn btn-default btn-sm', title: 'Excel'},
                    {extend: 'pdf', className: 'btn btn-default btn-sm', title: 'PDF'},
                    {extend: 'print', className: 'btn btn-default btn-sm', title: 'Print',
                     customize: function (win){
                            $(win.document.body).addClass('white-bg');
                            $(win.document.body).css('font-size', '15px');

                            $(win.document.body).find('table')
                                    .addClass('compact')
                                    .css('font-size', 'inherit');
                    	}
                    }
                ]

            });

        });

        function simpleLoad(btn, state) {
            if (state) {
                btn.children().addClass('fa-spin');
                btn.contents().last().replaceWith(" Loading");
            } else {
                setTimeout(function () {
                    btn.children().removeClass('fa-spin');
                    btn.contents().last().replaceWith(" Refresh");
                }, 2000);
            }
        }
