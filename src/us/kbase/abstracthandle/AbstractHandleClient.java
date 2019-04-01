package us.kbase.abstracthandle;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: AbstractHandle</p>
 * <pre>
 * A KBase module: AbstractHandle
 *   provides a programmatic access to a remote file store
 * </pre>
 */
public class AbstractHandleClient {
    private JsonClientCaller caller;
    private String serviceVersion = null;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public AbstractHandleClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public AbstractHandleClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public AbstractHandleClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Constructs a client with a custom URL
     * and a custom authorization service URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @param auth the URL of the authorization server.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public AbstractHandleClient(URL url, String user, String password, URL auth) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password, auth);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    public String getServiceVersion() {
        return this.serviceVersion;
    }

    public void setServiceVersion(String newValue) {
        this.serviceVersion = newValue;
    }

    /**
     * <p>Original spec-file function name: persist_handle</p>
     * <pre>
     * The persist_handle writes the handle to a persistent store that can be later retrieved using the list_handles function.
     * </pre>
     * @param   handle   instance of type {@link us.kbase.abstracthandle.Handle Handle}
     * @return   parameter "hid" of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String persistHandle(Handle handle, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(handle);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("AbstractHandle.persist_handle", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: hids_to_handles</p>
     * <pre>
     * Given a list of handle ids, this function returns a list of handles.
     * This method is replaced by fetch_handles_by.
     * </pre>
     * @param   hids   instance of list of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @return   parameter "handles" of list of type {@link us.kbase.abstracthandle.Handle Handle}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<Handle> hidsToHandles(List<String> hids, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hids);
        TypeReference<List<List<Handle>>> retType = new TypeReference<List<List<Handle>>>() {};
        List<List<Handle>> res = caller.jsonrpcCall("AbstractHandle.hids_to_handles", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: ids_to_handles</p>
     * <pre>
     * Given a list of ids, this function returns a list of handles.
     * In case of Shock, the list of ids are shock node ids.
     * This method is replaced by fetch_handles_by.
     * </pre>
     * @param   ids   instance of list of original type "NodeId"
     * @return   parameter "handles" of list of type {@link us.kbase.abstracthandle.Handle Handle}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<Handle> idsToHandles(List<String> ids, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(ids);
        TypeReference<List<List<Handle>>> retType = new TypeReference<List<List<Handle>>>() {};
        List<List<Handle>> res = caller.jsonrpcCall("AbstractHandle.ids_to_handles", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: fetch_handles_by</p>
     * <pre>
     * This function select records if field column entry is in elements and returns a list of handles.
     * </pre>
     * @param   params   instance of type {@link us.kbase.abstracthandle.FetchHandlesParams FetchHandlesParams}
     * @return   parameter "handles" of list of type {@link us.kbase.abstracthandle.Handle Handle}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<Handle> fetchHandlesBy(FetchHandlesParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<Handle>>> retType = new TypeReference<List<List<Handle>>>() {};
        List<List<Handle>> res = caller.jsonrpcCall("AbstractHandle.fetch_handles_by", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: is_owner</p>
     * <pre>
     * Given a list of handle ids, this function determines if the underlying data is owned by the caller.
     * If any one of the handle ids reference unreadable data this function returns false.
     * </pre>
     * @param   hids   instance of list of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long isOwner(List<String> hids, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hids);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.is_owner", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: delete_handles</p>
     * <pre>
     * The delete_handles function takes a list of handles and deletes them on the handle service server.
     * </pre>
     * @param   handles   instance of list of type {@link us.kbase.abstracthandle.Handle Handle}
     * @return   parameter "deleted_count" of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long deleteHandles(List<Handle> handles, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(handles);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.delete_handles", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: are_readable</p>
     * <pre>
     * Given a list of handle ids, this function determines if the underlying data is readable by the caller.
     * If any one of the handle ids reference unreadable data this function returns false.
     * </pre>
     * @param   hids   instance of list of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long areReadable(List<String> hids, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hids);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.are_readable", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: is_readable</p>
     * <pre>
     * Given a handle id, this function queries the underlying data store to see if the data being referred to is readable to by the caller.
     * </pre>
     * @param   hid   instance of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long isReadable(String hid, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hid);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.is_readable", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: add_read_acl</p>
     * <pre>
     * The add_read_acl function will update the acl of the shock node that the handle references.
     * The function is only accessible to a specific list of users specified at startup time.
     * The underlying shock node will be made readable to the user requested.
     * </pre>
     * @param   hids   instance of list of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @param   username   instance of String
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long addReadAcl(List<String> hids, String username, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hids);
        args.add(username);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.add_read_acl", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: set_public_read</p>
     * <pre>
     * The set_public_read function will update the acl of the shock node that the handle references to make the node globally readable.
     * The function is only accessible to a specific list of users specified at startup time.
     * </pre>
     * @param   hids   instance of list of original type "HandleId" (Handle provides a unique reference that enables access to the data files through functions provided as part of the HandleService. In the case of using shock, the id is the node id. In the case of using shock the value of type is shock. In the future these values should enumerated. The value of url is the http address of the shock server, including the protocol (http or https) and if necessary the port. The values of remote_md5 and remote_sha1 are those computed on the file in the remote data store. These can be used to verify uploads and downloads.)
     * @return   instance of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long setPublicRead(List<String> hids, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(hids);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("AbstractHandle.set_public_read", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    public Map<String, Object> status(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<Map<String, Object>>> retType = new TypeReference<List<Map<String, Object>>>() {};
        List<Map<String, Object>> res = caller.jsonrpcCall("AbstractHandle.status", args, retType, true, false, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }
}
