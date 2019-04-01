
package us.kbase.abstracthandle;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: FetchHandlesParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "elements",
    "field_name"
})
public class FetchHandlesParams {

    @JsonProperty("elements")
    private List<String> elements;
    @JsonProperty("field_name")
    private java.lang.String fieldName;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("elements")
    public List<String> getElements() {
        return elements;
    }

    @JsonProperty("elements")
    public void setElements(List<String> elements) {
        this.elements = elements;
    }

    public FetchHandlesParams withElements(List<String> elements) {
        this.elements = elements;
        return this;
    }

    @JsonProperty("field_name")
    public java.lang.String getFieldName() {
        return fieldName;
    }

    @JsonProperty("field_name")
    public void setFieldName(java.lang.String fieldName) {
        this.fieldName = fieldName;
    }

    public FetchHandlesParams withFieldName(java.lang.String fieldName) {
        this.fieldName = fieldName;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((("FetchHandlesParams"+" [elements=")+ elements)+", fieldName=")+ fieldName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
