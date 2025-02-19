import Joi from 'joi'

export const signUpSchema = Joi.object({
  username: Joi.string()
    .required()
    .label('Username')
    .messages({ 'string.empty': '{{#label}} is required' }),
  password: Joi.string()
    .min(3)
    .max(15)
    .required()
    .label('Password')
    .messages({ 'string.empty': '{{#label}} is required' }),
  confirm_password: Joi.any()
    .equal(Joi.ref('password'))
    .required()
    .label('Confirm Password')
    .messages({ 'any.only': '{{#label}} does not match' }),
  email: Joi.string()
    .email({ tlds: { allow: false } })
    .label('Email')
    .required()
    .messages({ 'string.empty': '{{#label}} is required' }),
  confirm_email: Joi.any()
    .equal(Joi.ref('email'))
    .required()
    .label('Confirm Email')
    .messages({ 'any.only': '{{#label}} does not match' }),
})
