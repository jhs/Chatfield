/**
 * CopilotKit integration for Chatfield
 * Allows using Chatfield interviews within CopilotKit conversations
 */

import React, { useState, useCallback, useEffect } from 'react'
import { useCopilotChat, useCopilotAction } from '@copilotkit/react-core'
import { useConversation } from './react'
import { ConversationInterface, FieldPreview } from './react-components'

export interface ChatfieldCopilotProps {
  interviews?: Record<string, Interview>
  onDataCollected?: (interviewName: string, data: any) => void
  className?: string
}

/**
 * CopilotKit component that integrates Chatfield interviews
 */
export function ChatfieldCopilot({ 
  interviews = {}, 
  onDataCollected, 
  className = '' 
}: ChatfieldCopilotProps) {
  const [activeInterview, setActiveInterview] = useState<string | null>(null)
  const [collectedData, setCollectedData] = useState<Record<string, any>>({})

  // Register actions with CopilotKit for each interview
  Object.entries(interviews).forEach(([name, interview]) => {
    useCopilotAction({
      name: `start_${name}_interviewing`,
      description: `Start collecting ${name} information through a conversation`,
      handler: async () => {
        setActiveInterview(name)
        return `Starting ${name} information interviewing...`
      }
    })
  })

  // Register preset actions
  useCopilotAction({
    name: "start_business_plan",
    description: "Start collecting business plan information",
    handler: async () => {
      setActiveInterview('business_plan')
      return "Starting business plan gathering..."
    }
  })

  useCopilotAction({
    name: "start_bug_report",
    description: "Start collecting bug report information",
    handler: async () => {
      setActiveInterview('bug_report')
      return "Starting bug report gathering..."
    }
  })

  useCopilotAction({
    name: "start_user_feedback",
    description: "Start collecting user feedback",
    handler: async () => {
      setActiveInterview('user_feedback')
      return "Starting user feedback collection..."
    }
  })

  useCopilotAction({
    name: "show_collected_data",
    description: "Show all collected data from previous conversations",
    handler: async () => {
      if (Object.keys(collectedData).length === 0) {
        return "No data has been collected yet."
      }
      
      let summary = "Here's what we've collected:\n\n"
      Object.entries(collectedData).forEach(([interviewName, data]) => {
        summary += `**${interviewName}:**\n`
        Object.entries(data).forEach(([field, value]) => {
          summary += `- ${field}: ${value}\n`
        })
        summary += "\n"
      })
      
      return summary
    }
  })

  const handleDataCollected = useCallback((interviewName: string, data: any) => {
    setCollectedData(prev => ({
      ...prev,
      [interviewName]: data
    }))
    setActiveInterview(null)
    onDataCollected?.(interviewName, data)
  }, [onDataCollected])

  // Get the current interview
  const getCurrentInterview = (): Interview | null => {
    if (!activeInterview) return null
    
    if (interviews[activeInterview]) {
      return interviews[activeInterview]
    }
    
    // Use presets
    switch (activeInterview) {
      case 'business_plan':
        return createInterview(schemaPresets.businessPlan())
      case 'bug_report':
        return createInterview(schemaPresets.bugReport())
      case 'user_feedback':
        return createInterview(schemaPresets.userFeedback())
      default:
        return null
    }
  }

  const currentInterview = getCurrentInterview()

  if (activeInterview && currentInterview) {
    return (
      <div className={`chatfield-copilot ${className}`}>
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">
            {activeInterview.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Collection
          </h3>
          <button
            onClick={() => setActiveInterview(null)}
            className="text-sm text-gray-600 hover:text-gray-800 underline"
          >
            ← Back to chat
          </button>
        </div>
        
        <ConversationInterface
          interview={currentInterview}
          onComplete={(data) => handleDataCollected(activeInterview, data)}
          onError={(error) => console.error('Interview error:', error)}
          className="h-96"
        />
      </div>
    )
  }

  return (
    <div className={`chatfield-copilot ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Data Collection Tools</h3>
        <p className="text-sm text-gray-600 mb-4">
          Available gathering tools you can activate through conversation:
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Built-in presets */}
        <InterviewCard
          name="Business Plan"
          description="Collect comprehensive business plan information"
          onClick={() => setActiveInterview('business_plan')}
          interview={createInterview(schemaPresets.businessPlan())}
        />
        
        <InterviewCard
          name="Bug Report"
          description="Gather detailed bug report information"
          onClick={() => setActiveInterview('bug_report')}
          interview={createInterview(schemaPresets.bugReport())}
        />
        
        <InterviewCard
          name="User Feedback"
          description="Collect user feedback and suggestions"
          onClick={() => setActiveInterview('user_feedback')}
          interview={createInterview(schemaPresets.userFeedback())}
        />
        
        {/* Custom interviews */}
        {Object.entries(interviews).map(([name, interview]) => (
          <InterviewCard
            key={name}
            name={name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            description={`Custom ${name} data collection`}
            onClick={() => setActiveInterview(name)}
            interview={interview}
          />
        ))}
      </div>

      {Object.keys(collectedData).length > 0 && (
        <div className="border-t pt-4">
          <h4 className="font-semibold mb-2">Previously Collected Data:</h4>
          <div className="space-y-2">
            {Object.entries(collectedData).map(([name, data]) => (
              <div key={name} className="bg-gray-50 p-3 rounded">
                <div className="font-medium text-sm text-gray-700">{name}</div>
                <div className="text-xs text-gray-500">
                  {Object.keys(data).length} fields collected
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

interface InterviewCardProps {
  name: string
  description: string
  onClick: () => void
  interview: Interview
}

function InterviewCard({ name, description, onClick, interview }: InterviewCardProps) {
  const [showPreview, setShowPreview] = useState(false)
  const fieldCount = interview.getFieldPreview().length

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-medium text-gray-900">{name}</h4>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {fieldCount} fields
        </span>
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{description}</p>
      
      <div className="flex space-x-2">
        <button
          onClick={onClick}
          className="flex-1 px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
        >
          Start
        </button>
        
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="px-3 py-2 text-gray-600 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          {showPreview ? 'Hide' : 'Preview'}
        </button>
      </div>
      
      {showPreview && (
        <div className="mt-3 pt-3 border-t">
          <FieldPreview interview={interview} className="border-0 p-0" />
        </div>
      )}
    </div>
  )
}

/**
 * Hook for using Chatfield within CopilotKit conversations
 */
export function useChatfieldCopilot() {
  const [activeInterviews, setActiveInterviews] = useState<Record<string, Interview>>({})
  const [interviewInstances, setInterviewInstances] = useState<Record<string, InterviewInstance>>({})

  const startInterviewing = useCallback((name: string, interview: Interview) => {
    setActiveInterviews(prev => ({ ...prev, [name]: interview }))
  }, [])

  const completeInterviewing = useCallback((name: string, instance: InterviewInstance) => {
    setInterviewInstances(prev => ({ ...prev, [name]: instance }))
    setActiveInterviews(prev => {
      const { [name]: _, ...rest } = prev
      return rest
    })
  }, [])

  const getAllData = useCallback(() => {
    return Object.fromEntries(
      Object.entries(interviewInstances).map(([name, instance]) => [
        name,
        instance.getData()
      ])
    )
  }, [interviewInstances])

  return {
    activeInterviews,
    interviewInstances,
    startInterviewing,
    completeInterviewing,
    getAllData,
    hasActiveInterviews: Object.keys(activeInterviews).length > 0,
    hasCompletedData: Object.keys(interviewInstances).length > 0
  }
}

/**
 * CopilotKit action registrar for dynamic interview setup
 */
export function registerChatfieldActions(
  interviews: Record<string, Interview>,
  options: {
    onInterviewStart?: (name: string) => void
    onInterviewComplete?: (name: string, data: any) => void
  } = {}
) {
  return Object.entries(interviews).map(([name, interview]) => {
    return {
      name: `collect_${name}`,
      description: `Start collecting ${name} information through an interactive conversation`,
      handler: async () => {
        options.onInterviewStart?.(name)
        return `Starting ${name} information collection. This will guide you through a conversational form to gather all necessary details.`
      }
    }
  })
}

/**
 * Chatfield-powered CopilotKit sidebar component
 */
export function ChatfieldSidebar({ 
  interviews = {},
  className = '' 
}: {
  interviews?: Record<string, Interview>
  className?: string
}) {
  const {
    activeInterviews,
    interviewInstances,
    startInterviewing,
    completeInterviewing,
    getAllData
  } = useChatfieldCopilot()

  // Register actions for all interviews
  Object.entries(interviews).forEach(([name, interview]) => {
    useCopilotAction({
      name: `collect_${name}`,
      description: `Collect ${name} information through conversation`,
      handler: async () => {
        startInterviewing(name, interview)
        return `Starting ${name} collection...`
      }
    })
  })

  // Register data export action
  useCopilotAction({
    name: "export_collected_data",
    description: "Export all collected data as JSON",
    handler: async () => {
      const data = getAllData()
      return JSON.stringify(data, null, 2)
    }
  })

  const activeInterviewEntries = Object.entries(activeInterviews)

  return (
    <div className={`chatfield-sidebar ${className}`}>
      {activeInterviewEntries.length > 0 ? (
        <div className="space-y-4">
          {activeInterviewEntries.map(([name, interview]) => (
            <div key={name} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold mb-2">
                Collecting: {name.replace('_', ' ')}
              </h3>
              
              <ConversationInterface
                interview={interview}
                onComplete={(data) => {
                  const instance = new InterviewInstance(interview.getMeta(), data)
                  completeInterviewing(name, instance)
                }}
                className="h-80"
              />
            </div>
          ))}
        </div>
      ) : (
        <ChatfieldCopilot 
          interviews={interviews}
          onDataCollected={(name, data) => console.log(`Collected ${name}:`, data)}
          className={className}
        />
      )}
    </div>
  )
}