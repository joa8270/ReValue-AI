-- Create a table for storing valuation history
create table history (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users not null,
  specs jsonb not null,
  valuation jsonb not null,
  ai_advice text,
  created_at timestamptz default now()
);

-- Enable Row Level Security (RLS)
alter table history enable row level security;

-- Create a policy that allows users to view their own history
create policy "Users can view their own history"
on history for select
using ( auth.uid() = user_id );

-- Create a policy that allows users to insert their own history
create policy "Users can insert their own history"
on history for insert
with check ( auth.uid() = user_id );

-- Create a policy that allows users to delete their own history (optional)
create policy "Users can delete their own history"
on history for delete
using ( auth.uid() = user_id );
