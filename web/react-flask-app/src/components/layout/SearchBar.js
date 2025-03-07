import React from "react";
import PropTypes from "prop-types";
import classnames from "classnames";

const SearchBar = ({
  label,
  name,
  value,
  placeholder,
  onChange,
  error,
}) => {
  return (
    <div className="form-group">
      <input 
      type="text" 
      name={name}
      classname={classnames("form-control form-control-lg", {"is-invalid": error,})}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      />
      {error && <div className="invalid-feedback">{error}</div>}
    </div>
  );
}

SearchBar.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string.isRequired,
};


export default SearchBar;