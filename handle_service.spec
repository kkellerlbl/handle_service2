/*
A KBase module: AbstractHandle
  provides a programmatic access to a remote file store
*/

module AbstractHandle {

    /* Handle provides a unique reference that enables
       access to the data files through functions
       provided as part of the HandleService. In the case of using
       shock, the id is the node id. In the case of using
       shock the value of type is shock. In the future
       these values should enumerated. The value of url is
       the http address of the shock server, including the
       protocol (http or https) and if necessary the port.
       The values of remote_md5 and remote_sha1 are those
       computed on the file in the remote data store. These
       can be used to verify uploads and downloads.
    */
    typedef string HandleId;
    typedef string NodeId;

    typedef structure {
      HandleId hid;
      string file_name;
      NodeId id;
      string type;
      string url;
      string remote_md5;
      string remote_sha1;
    } Handle;

    /*
      The persist_handle writes the handle to a persistent store that can be later retrieved using the list_handles function.
    */
    funcdef persist_handle(Handle h) returns (string hid) authentication required;

    /*
      Given a list of handle ids, this function returns a list of handles.
      This method is replaced by fetch_handles_by.
    */
    funcdef hids_to_handles(list<HandleId> hids) returns(list<Handle> handles)  authentication required;

    /*
      Given a list of ids, this function returns a list of handles.
      In case of Shock, the list of ids are shock node ids.
      This method is replaced by fetch_handles_by.
    */
    funcdef ids_to_handles(list<NodeId> ids) returns (list<Handle> handles) authentication required;

    typedef structure {
      list<string> elements;
      string key;
    } FetchHandlesParams;

    /*
      This function select records if key column entry is in elements and returns a list of handles.
    */
    funcdef fetch_handles_by(FetchHandlesParams params) returns (list<Handle> handles) authentication required;

    /*
      Given a list of handle ids, this function determines if the underlying data is owned by the caller.
      If any one of the handle ids reference unreadable data this function returns false.
    */
    funcdef is_owner(list<HandleId>) returns(int) authentication required;

    /*
      The delete_handles function takes a list of handles and deletes them on the handle service server.
    */
    funcdef delete_handles(list<Handle> handles) returns (list<HandleId> removed_hids) authentication optional;

    /*
      Given a list of handle ids, this function determines if the underlying data is readable by the caller.
      If any one of the handle ids reference unreadable data this function returns false.
    */
    funcdef are_readable(list<HandleId> hids) returns(int) authentication required;

    /*
      Given a handle id, this function queries the underlying data store to see if the data being referred to is readable to by the caller.
    */
    funcdef is_readable(HandleId hid) returns(int) authentication required;

};
