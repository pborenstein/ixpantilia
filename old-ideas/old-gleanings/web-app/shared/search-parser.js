/**
 * Search Query Parser
 * Extracts operators from search strings like "domain:github.com before:2023-01-01 typescript"
 */

export function parseSearchQuery(searchString) {
  if (!searchString || typeof searchString !== 'string') {
    return {
      operators: {},
      text: ''
    }
  }

  const operators = {}
  const words = []
  
  // Split by spaces but preserve quoted strings
  const tokens = searchString.match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) || []
  
  tokens.forEach(token => {
    // Remove quotes if present
    const cleanToken = token.replace(/^["']|["']$/g, '')
    
    // Check if token is an operator (contains colon)
    const operatorMatch = cleanToken.match(/^([a-zA-Z]+):(.+)$/)
    
    if (operatorMatch) {
      const [, operator, value] = operatorMatch
      const normalizedOperator = operator.toLowerCase()
      
      // Only accept known operators
      if (['domain', 'before', 'after', 'status', 'category'].includes(normalizedOperator)) {
        // Handle multiple values by splitting on commas
        if (normalizedOperator === 'category' || normalizedOperator === 'domain') {
          const values = value.split(',').map(v => v.trim()).filter(v => v)
          if (values.length > 1) {
            operators[normalizedOperator] = values
          } else {
            operators[normalizedOperator] = value.trim()
          }
        } else {
          operators[normalizedOperator] = value.trim()
        }
      } else {
        // Unknown operator, treat as regular text
        words.push(cleanToken)
      }
    } else {
      words.push(cleanToken)
    }
  })

  return {
    operators,
    text: words.join(' ').trim()
  }
}

/**
 * Convert parsed query back to search string
 */
export function buildSearchQuery(operators, text) {
  const parts = []
  
  // Add operators
  Object.entries(operators).forEach(([key, value]) => {
    if (value && value !== 'all') {
      // Handle arrays for multi-value operators
      if (Array.isArray(value)) {
        const joinedValue = value.join(',')
        const quotedValue = joinedValue.includes(' ') ? `"${joinedValue}"` : joinedValue
        parts.push(`${key}:${quotedValue}`)
      } else {
        // Quote values that contain spaces
        const quotedValue = value.includes(' ') ? `"${value}"` : value
        parts.push(`${key}:${quotedValue}`)
      }
    }
  })
  
  // Add text
  if (text) {
    parts.push(text)
  }
  
  return parts.join(' ')
}

/**
 * Get available operator suggestions for autocomplete
 */
export function getOperatorSuggestions() {
  return [
    { operator: 'domain', description: 'Filter by domain (e.g., domain:github.com)' },
    { operator: 'before', description: 'Show items before date (e.g., before:2023-01-01)' },
    { operator: 'after', description: 'Show items after date (e.g., after:2023-01-01)' },
    { operator: 'status', description: 'Filter by status (e.g., status:active, status:hidden)' },
    { operator: 'category', description: 'Filter by category (e.g., category:tech)' }
  ]
}

/**
 * Validate date format (YYYY-MM-DD)
 */
export function isValidDate(dateString) {
  if (!dateString) return false
  
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(dateString)) return false
  
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date.getTime())
}

/**
 * Parse and validate operators
 */
export function validateOperators(operators) {
  const validated = { ...operators }
  const errors = []
  
  // Validate date operators
  if (validated.before && !isValidDate(validated.before)) {
    errors.push(`Invalid date format for 'before': ${validated.before}. Use YYYY-MM-DD format.`)
    delete validated.before
  }
  
  if (validated.after && !isValidDate(validated.after)) {
    errors.push(`Invalid date format for 'after': ${validated.after}. Use YYYY-MM-DD format.`)
    delete validated.after
  }
  
  // Validate status operator
  if (validated.status && !['active', 'hidden', 'all'].includes(validated.status)) {
    errors.push(`Invalid status: ${validated.status}. Must be 'active', 'hidden', or 'all'.`)
    delete validated.status
  }
  
  return {
    operators: validated,
    errors
  }
}