/*
A KBase module: handle_service
*/

module handle_service {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_handle_service(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
