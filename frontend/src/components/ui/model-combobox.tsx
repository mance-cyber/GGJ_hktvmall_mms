"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export interface FetchedModelOption {
  id: string
  name: string
  owned_by?: string
}

export interface PresetModelOption {
  id: string
  name: string
  description?: string
}

interface ModelComboboxProps {
  value: string
  onValueChange: (value: string) => void
  fetchedModels?: FetchedModelOption[]
  presetModels?: PresetModelOption[]
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  className?: string
}

export function ModelCombobox({
  value,
  onValueChange,
  fetchedModels = [],
  presetModels = [],
  placeholder = "選擇模型...",
  searchPlaceholder = "搜尋模型...",
  emptyText = "找不到符合的模型",
  className,
}: ModelComboboxProps) {
  const [open, setOpen] = React.useState(false)

  const getDisplayName = () => {
    if (!value) return placeholder
    
    const fetchedModel = fetchedModels.find((m) => m.id === value)
    if (fetchedModel) return fetchedModel.name
    
    const presetModel = presetModels.find((m) => m.id === value)
    if (presetModel) return presetModel.name
    
    return value
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between font-normal",
            !value && "text-muted-foreground",
            className
          )}
        >
          <span className="truncate">{getDisplayName()}</span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
        <Command>
          <CommandInput placeholder={searchPlaceholder} />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            
            {fetchedModels.length > 0 && (
              <CommandGroup heading={
                <span className="text-green-600">
                  ✓ API 可用模型 ({fetchedModels.length})
                </span>
              }>
                {fetchedModels.map((model) => (
                  <CommandItem
                    key={`fetched-${model.id}`}
                    value={`${model.id} ${model.name}`}
                    onSelect={() => {
                      onValueChange(model.id)
                      setOpen(false)
                    }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{model.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {model.owned_by || model.id}
                      </span>
                    </div>
                    <Check
                      className={cn(
                        "h-4 w-4 shrink-0",
                        value === model.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
            
            {presetModels.length > 0 && (
              <CommandGroup heading="預設模型">
                {presetModels.map((model) => (
                  <CommandItem
                    key={`preset-${model.id}`}
                    value={`${model.id} ${model.name}`}
                    onSelect={() => {
                      onValueChange(model.id)
                      setOpen(false)
                    }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{model.name}</span>
                      {model.description && (
                        <span className="text-xs text-muted-foreground">
                          {model.description}
                        </span>
                      )}
                    </div>
                    <Check
                      className={cn(
                        "h-4 w-4 shrink-0",
                        value === model.id ? "opacity-100" : "opacity-0"
                      )}
                    />
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
