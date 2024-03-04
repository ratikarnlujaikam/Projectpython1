import * as React from 'react';
interface ICheckboxProps {
    disabled?: boolean;
    value: any;
}
interface ICheckboxGroupProps {
    children: (Checkbox: React.FC<ICheckboxProps>) => JSX.Element;
    name: string;
    value: any[];
    onChange: (newValue: any[]) => any;
}
declare const CheckboxGroup: React.FC<ICheckboxGroupProps>;
export default CheckboxGroup;
