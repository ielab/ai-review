import Joi from 'joi'

import { IJobForm } from '@/types/data'

const jobSchema = Joi.object({
  name: Joi.string().required().max(150).messages({
    'string.empty': 'Job name is required',
    'string.max': 'Job name is too long (max 150 characters)',
  }),
  selection_method_id: Joi.number().required().messages({
    'number.base': 'Selection method is required',
    'number.empty': 'Selection method is required',
    'number.required': 'Selection method is required',
    'any.required': 'Selection method is required',
  }),
})

export const validateJob = (data: IJobForm) => {
  return jobSchema.validate(data, { abortEarly: false })
}
