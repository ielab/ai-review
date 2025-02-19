import Joi from 'joi'

export const loginSchema = Joi.object({
  identifier: Joi.string()
    .required()
    .label('Username/Email')
    .messages({ 'string.empty': '{{#label}} is required' }),
  password: Joi.string()
    .required()
    .label('Password')
    .messages({ 'string.empty': '{{#label}} is required' }),
})
